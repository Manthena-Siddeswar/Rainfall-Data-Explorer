from pathlib import Path
import pandas as pd

DATA_DIR = Path("data")
CSV_PATH = DATA_DIR / "rainfall_records.csv"
JSON_PATH = DATA_DIR / "rainfall_records.json"
COLUMNS = ["record_id", "date", "location", "rainfall_mm", "weather_condition", "remarks"]

def load_records():
    DATA_DIR.mkdir(exist_ok=True)
    if CSV_PATH.exists():
        try:
            df = pd.read_csv(CSV_PATH)
            for col in COLUMNS:
                if col not in df.columns:
                    df[col] = ""
            return df[COLUMNS]
        except Exception:
            pass
    if JSON_PATH.exists():
        try:
            df = pd.read_json(JSON_PATH)
            for col in COLUMNS:
                if col not in df.columns:
                    df[col] = ""
            return df[COLUMNS]
        except Exception:
            pass
    return pd.DataFrame(columns=COLUMNS)

def save_records(df):
    DATA_DIR.mkdir(exist_ok=True)
    clean = df.copy()
    for col in COLUMNS:
        if col not in clean.columns:
            clean[col] = ""
    clean = clean[COLUMNS]
    clean.to_csv(CSV_PATH, index=False)
    clean.to_json(JSON_PATH, orient="records", indent=2)

def validate_import_dataframe(df, existing):
    errors = []
    missing = [c for c in COLUMNS if c not in df.columns]
    if missing:
        return False, [f"Missing required column(s): {', '.join(missing)}"], pd.DataFrame(columns=COLUMNS)
    clean = df[COLUMNS].copy()
    for col in ["record_id", "date", "location", "weather_condition", "remarks"]:
        clean[col] = clean[col].fillna("").astype(str).str.strip()
    clean["rainfall_mm"] = pd.to_numeric(clean["rainfall_mm"], errors="coerce")
    if clean["record_id"].eq("").any(): errors.append("Record IDs cannot be blank.")
    if clean["location"].eq("").any(): errors.append("Location cannot be blank.")
    if clean["date"].eq("").any(): errors.append("Date cannot be blank.")
    if clean["record_id"].duplicated().any(): errors.append("Duplicate record IDs found within the uploaded file.")
    existing_ids = set(existing["record_id"].astype(str)) if not existing.empty else set()
    duplicate_ids = sorted(set(clean["record_id"]) & existing_ids)
    if duplicate_ids: errors.append("These record IDs already exist: " + ", ".join(duplicate_ids))
    if clean["rainfall_mm"].isna().any(): errors.append("Rainfall values must be valid numbers.")
    elif (clean["rainfall_mm"] < 0).any(): errors.append("Rainfall cannot be negative.")
    elif (clean["rainfall_mm"] > 2000).any(): errors.append("Rainfall cannot exceed 2000 mm per record.")
    try:
        parsed = pd.to_datetime(clean["date"], errors="coerce")
        if parsed.isna().any(): errors.append("One or more dates are invalid. Use YYYY-MM-DD.")
        else: clean["date"] = parsed.dt.strftime("%Y-%m-%d")
    except Exception:
        errors.append("Could not validate date values.")
    return len(errors) == 0, errors, clean
