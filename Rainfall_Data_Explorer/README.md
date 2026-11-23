# Rainfall Data Explorer

## Run on Windows
1. Extract the ZIP.
2. Open the `Rainfall_Data_Explorer` folder in VS Code.
3. Open Terminal in VS Code.
4. Run these commands:

```powershell
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Demo login
- Username: `admin`
- Password: `rainfall123`

This is a simple demonstration login for a college project, not production-grade authentication. Change the credentials in `app.py` before any public deployment.

## Data
The sample CSV contains 40 illustrative records. Import it from the **Data Import** page. These are not official meteorological measurements.
