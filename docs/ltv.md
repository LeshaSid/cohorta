---
title: Ltv
marimo-version: 0.23.13
---

```python {.marimo}
import marimo as mo
import psycopg2
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
```

```python {.marimo}
with open("sql/ltv.sql", "r", encoding="utf-8") as f:
    query = f.read()

conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5433/cohorta_db")
df = pd.read_sql_query(query, conn)
conn.close()

cohort_sizes = df[df["period_number"] == 0][["cohort_date","user_count"]].rename(columns={"user_count": "cohort_size"})
df_with_size = df.merge(cohort_sizes, on="cohort_date", how="left")
df_with_size["cumulative_revenue"] = df_with_size.groupby('cohort_date')['revenue_sum'].cumsum()
df_with_size["ltv"] = df_with_size["cumulative_revenue"] / df_with_size["cohort_size"]

top_cohorts = df_with_size['cohort_date'].unique()[0:10]
df_plot = df_with_size[df_with_size['cohort_date'].isin(top_cohorts)]
plt.figure(figsize=(8, 5))
sns.lineplot(data=df_plot, x="period_number", y="ltv", hue="cohort_date")
plt.title("Кривые LTV по когортам")
plt.xlabel("Дни жизни(period_number)")
plt.ylabel("LTV(накопленная выручка на пользователя)")
plt.show()
```

!(LTV)[images/ltv.png]