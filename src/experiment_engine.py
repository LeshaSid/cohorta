import marimo

__generated_with = "0.23.13"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import numpy as np
    import pandas as pd
    import psycopg2
    from statsmodels.stats.proportion import proportions_ztest

    return np, pd, proportions_ztest, psycopg2


@app.cell
def _(np):
    def bootstrap(revenue_A, revenue_B, n_bootstrap_samples=2000):
        boot_differences = []
        size_A = len(revenue_A)
        size_B = len(revenue_B)

        for i in range(n_bootstrap_samples):
            sample_A = np.random.choice(revenue_A, size=size_A, replace=True)
            sample_B = np.random.choice(revenue_B, size=size_B, replace=True)

            mean_A = np.mean(sample_A)
            mean_B = np.mean(sample_B)

            diff = mean_B - mean_A
            boot_differences.append(diff)

        return boot_differences

    return (bootstrap,)


@app.cell
def _(np):
    def analyze_bootstrap_result(boot_differences, alpha=0.05):
        left_percentile = np.percentile(boot_differences, (alpha / 2) * 100)
        right_percentile = np.percentile(boot_differences, (1 - alpha / 2) * 100)
        print(f"Доверительный интервал: [{left_percentile}, {right_percentile}]")
        if left_percentile > 0:
            print("Тест успешен! Эффект значимо положительный.")
        elif right_percentile < 0:
            print("Тест значимо ухудшил метрику")
        else:
            print("Изменений нет")

    return (analyze_bootstrap_result,)


@app.cell
def _(proportions_ztest):
    def analyze_conversion(df, alpha=0.05):
        n_A = df[df['group_ab'] == 'A'].shape[0]
        n_B = df[df['group_ab'] == 'B'].shape[0]
    
        success_A = df[(df['group_ab'] == 'A') & (df['count_purchases'] > 0)].shape[0]
        success_B = df[(df['group_ab'] == 'B') & (df['count_purchases'] > 0)].shape[0]
    
        cr_A = success_A / n_A
        cr_B = success_B / n_B
        print(f"Конверсия в группе А: {cr_A:.2%}")
        print(f"Конверсия в группе Б: {cr_B:.2%}")
    
        z_stat, p_value = proportions_ztest([success_B, success_A], [n_B, n_A])
        print(f"Z-statistic: {z_stat:.4f}, P-value: {p_value:.4f}")

        if p_value < alpha:
            if cr_B > cr_A:
                print("Тест успешен! Конверсия значимо выросла.")
            else:
                print("Внимание! Конверсия значимо упала.")
        else:
            print("Изменений в конверсии нет (статистически значимых различий не обнаружено).")



    return (analyze_conversion,)


@app.cell
def _(analyze_bootstrap_result, analyze_conversion, bootstrap, pd, psycopg2):
    with open("sql/ab_test.sql", "r", encoding="utf-8") as f:
        query = f.read()

    conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5433/cohorta_db")
    df = pd.read_sql_query(query, conn)
    conn.close()

    revenue_A = df[df["group_ab"] == "A"]["sum_revenue"]
    revenue_B = df[df["group_ab"] == "B"]["sum_revenue"]

    boot_diffs = bootstrap(revenue_A, revenue_B)
    analyze_bootstrap_result(boot_diffs)

    paying_users = df[df['count_purchases'] > 0]

    aov_A = paying_users[paying_users['group_ab'] == 'A']['sum_revenue'] / paying_users[paying_users['group_ab'] == 'A']['count_purchases']

    aov_B = paying_users[paying_users['group_ab'] == 'B']['sum_revenue'] / paying_users[paying_users['group_ab'] == 'B']['count_purchases']

    boot_diffs_aov = bootstrap(aov_A, aov_B)
    analyze_bootstrap_result(boot_diffs_aov)
    analyze_conversion(df)
    return


if __name__ == "__main__":
    app.run()
