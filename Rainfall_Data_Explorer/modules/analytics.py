import pandas as pd

def get_summary(df):
    vals = pd.to_numeric(df["rainfall_mm"], errors="coerce").dropna()
    dates = pd.to_datetime(df["date"], errors="coerce").dropna()
    date_range = f"{dates.min().date()} to {dates.max().date()}" if len(dates) else "Not available"
    return {
        "total": float(vals.sum()) if len(vals) else 0.0,
        "average": float(vals.mean()) if len(vals) else 0.0,
        "maximum": float(vals.max()) if len(vals) else 0.0,
        "minimum": float(vals.min()) if len(vals) else 0.0,
        "count": int(len(df)),
        "locations": int(df["location"].nunique()),
        "date_range": date_range
    }

def monthly_summary(df):
    if df.empty:
        return pd.DataFrame(columns=["month", "rainfall_mm"])
    work = df.copy()
    work["date"] = pd.to_datetime(work["date"], errors="coerce")
    work["rainfall_mm"] = pd.to_numeric(work["rainfall_mm"], errors="coerce")
    work = work.dropna(subset=["date", "rainfall_mm"])
    if work.empty:
        return pd.DataFrame(columns=["month", "rainfall_mm"])
    work["month"] = work["date"].dt.to_period("M").astype(str)
    return work.groupby("month", as_index=False)["rainfall_mm"].sum()
