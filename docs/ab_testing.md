# Резюме
## Что проверяли
Проверяли скдку в размере 15%
## Ключевая метрика
Ключевыми метриками стали конверсия, средняя выручка и средний чек на пользователя
## Итог
Мы наблюдаем рост конверсии 2.12% в группе В, рост средней выручки на 24% и падение среднего чека на пользователя на 14.6%. Это может свидетельствовать о том, что пользователи стали покупать чаще, но более дешёвые товары, из-за этого и падает средний чек, однако из-за объёма покупок выручка выросла. Доверительный интервал для разницы средних выручек: [26.36, 35.75] — полностью положительный, значит рост выручки статистически значим.

```python {.marimo}
import marimo as mo
import numpy as np
import pandas as pd
import psycopg2
from statsmodels.stats.proportion import proportions_ztest
import seaborn as sb
import matplotlib.pyplot as plt
```

```python {.marimo}
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
```

```python {.marimo}
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
    return left_percentile, right_percentile
```

```python {.marimo}
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
    return n_A, n_B, cr_A, cr_B, p_value
```

```python {.marimo}
with open("sql/ab_test.sql", "r", encoding="utf-8") as f:
    query = f.read()

conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5433/cohorta_db")
df = pd.read_sql_query(query, conn)
conn.close()

revenue_A = df[df["group_ab"] == "A"]["sum_revenue"]
revenue_B = df[df["group_ab"] == "B"]["sum_revenue"]

boot_diffs = bootstrap(revenue_A, revenue_B)
left_percentile_revenue, right_percentile_revenue = analyze_bootstrap_result(boot_diffs)

paying_users = df[df['count_purchases'] > 0]

aov_A = paying_users[paying_users['group_ab'] == 'A']['sum_revenue'] / paying_users[paying_users['group_ab'] == 'A']['count_purchases']

aov_B = paying_users[paying_users['group_ab'] == 'B']['sum_revenue'] / paying_users[paying_users['group_ab'] == 'B']['count_purchases']

boot_diffs_aov = bootstrap(aov_A, aov_B)
left_percentile_aov, right_percentile_aov = analyze_bootstrap_result(boot_diffs_aov)
n_A, n_B, p_A, p_B, p_value = analyze_conversion(df)
se_A = np.sqrt(p_A * (1 - p_A) / n_A)
se_B = np.sqrt(p_B * (1 - p_B) / n_B)
lower_A = p_A - 1.96 * se_A
lower_B = p_B - 1.96 * se_B
upper_A = p_A + 1.96 * se_A
upper_B = p_B + 1.96 * se_B
groups = ["A", "B"]
conversions = [p_A, p_B]
errors = [se_A*1.96, se_B*1.96]
```

```python {.marimo}
revenue_paying_A = df[(df["group_ab"] == "A") & (df['count_purchases'] > 0)]["sum_revenue"]
revenue_paying_B = df[(df["group_ab"] == "B") & (df['count_purchases'] > 0)]["sum_revenue"]
df_revenue = pd.DataFrame({
    "group" : ["A"]*len(revenue_paying_A) + ["B"]*len(revenue_paying_B),
    "revenue" : list(revenue_paying_A) + list(revenue_paying_B)
})

df_aov = pd.DataFrame({
    "group" : ["A"]*len(aov_A) + ["B"]*len(aov_B),
    "aov" : list(aov_A) + list(aov_B)
})
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
sb.boxplot(data=df_revenue, x="group", y="revenue", ax=axes[0], color="red")
sb.boxplot(data=df_aov, x="group", y="aov", ax=axes[1])
axes[0].set_title("Revenue")
axes[1].set_title("AOV")
plt.figure(figsize=(4, 5))
plt.bar(x=groups, height=conversions, yerr=errors, capsize=5, width=0.4)
plt.xlabel("group")
plt.ylabel("conversion")
plt.title("Conversion")
plt.show()
```

!(Revenue and AOV)[../images/revenue_aov.png]

!(Conversion)[../images/conversion.png]

!(Result)[../images/ab_test_result.png]