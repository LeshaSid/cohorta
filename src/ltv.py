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
    import numpy as np

    return pd, psycopg2


@app.cell
def _(pd, psycopg2):
    with open("sql/ltv.sql", "r", encoding="utf-8") as f:
        query = f.read()

    conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5433/cohorta_db")
    df = pd.read_sql_query(query, conn)
    conn.close()

    cohort_sizes = df[df["period_number"] == 0][["cohort_date","user_count"]].rename(columns={"user_count": "cohort_size"})
    df_with_size = df.merge(cohort_sizes, on="cohort_date", how="left")
    df_with_size["cumulative_revenue"] = df_with_size.groupby('cohort_date')['revenue_sum'].cumsum()
    df_with_size["ltv"] = df_with_size["cumulative_revenue"] / df_with_size["cohort_size"]
    return


if __name__ == "__main__":
    app.run()
