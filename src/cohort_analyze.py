import marimo

__generated_with = "0.23.13"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import psycopg2
    import pandas as pd
    import seaborn as sns
    import matplotlib.pyplot as plt

    return pd, plt, psycopg2, sns


@app.cell
def _(pd, plt, psycopg2, sns):
    with open("sql/cohorts.sql", "r", encoding="utf-8") as f:
        query = f.read()

    conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5433/cohorta_db")
    df = pd.read_sql_query(query, conn)
    conn.close()

    cohort_sizes = df[df["period_number"] == 0][["cohort_date","user_count"]].rename(columns={"user_count": "cohort_size"})
    df_with_size = df.merge(cohort_sizes, on="cohort_date", how="left")
    df_with_size["retention"] = df_with_size["user_count"] / df_with_size["cohort_size"] * 100
    pivot_df = df_with_size.pivot(index="cohort_date", columns="period_number", values="retention")
    plt.figure(figsize=(12, 8))
    sns.heatmap(pivot_df, annot=True, fmt=".1f", cmap="Blues")
    plt.title("Retention by Cohorts")
    plt.show()
    return


if __name__ == "__main__":
    app.run()
