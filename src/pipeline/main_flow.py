from prefect import task, flow
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.ensemble import IsolationForest, RandomForestRegressor
import datetime

DB_CONNECTION = 'postgresql://postgres:T4e!fsF#GY3@localhost:5432/Anomaly_db'


@task(name="Ingest Data")
def fetch_data():
    """Simulates fetching new data (e.g., usually run daily)."""
    # For simulation, we generate "Tomorrow's" data based on "Today"
    now = datetime.datetime.now()
    # Let's pretend we are fetching the last 24h
    date_range = pd.date_range(end=now, periods=24, freq='h')

    # Synthetic pattern
    x = np.linspace(0, 4 * np.pi, 24)
    load = 500 + 200 * np.sin(x) + np.random.normal(0, 15, 24)

    # Random anomaly
    if np.random.rand() > 0.8:
        load[15] += 300

    return pd.DataFrame({'timestamp': date_range, 'load_value': load})


@task(name="Process & Model")
def run_models(new_data: pd.DataFrame):
    """
    1. Reads OLD history from DB.
    2. Combines with NEW data.
    3. Retrains models (Anomaly + Forecast).
    """
    engine = create_engine(DB_CONNECTION)

    # 1. Get History
    try:
        history = pd.read_sql("SELECT * FROM energy_data", engine)
        # Drop old predictions if they exist in the read DF to avoid schema mismatch
        if 'predicted_load' in history.columns:
            history = history.drop(columns=['predicted_load'])
    except:
        history = pd.DataFrame()

    # 2. Combine Data
    full_df = pd.concat([history, new_data]).drop_duplicates(subset=['timestamp']).sort_values('timestamp')

    # 3. Anomaly Detection (Isolation Forest)
    iso = IsolationForest(contamination=0.02)
    full_df['is_anomaly'] = iso.fit_predict(full_df[['load_value']])
    full_df['is_anomaly'] = full_df['is_anomaly'] == -1

    # 4. Forecasting (Random Forest)
    # Feature Engineering
    df_train = full_df.copy()
    df_train['hour'] = df_train['timestamp'].dt.hour
    df_train['dayofweek'] = df_train['timestamp'].dt.dayofweek

    rf = RandomForestRegressor(n_estimators=50)
    rf.fit(df_train[['hour', 'dayofweek']], df_train['load_value'])

    # Predict for the *new* data we just ingested to fill the 'predicted_load' column
    # (In a real scenario, you'd predict future, but here we fill the DB column)
    new_data_features = new_data.copy()
    new_data_features['hour'] = new_data_features['timestamp'].dt.hour
    new_data_features['dayofweek'] = new_data_features['timestamp'].dt.dayofweek

    full_df.loc[full_df['timestamp'].isin(new_data['timestamp']), 'predicted_load'] = rf.predict(
        new_data_features[['hour', 'dayofweek']])

    return full_df


@task(name="Save to DB")
def save_to_db(df: pd.DataFrame):
    engine = create_engine(DB_CONNECTION)
    # We use 'replace' here to update the whole history with new anomaly flags
    # In huge production systems, you would use 'append', but for this project 'replace' keeps it simple and clean.
    df.to_sql('energy_data', engine, if_exists='replace', index=False)
    print(f"💾 Database updated. Total rows: {len(df)}")


@flow(name="Energy Pipeline")
def main_flow():
    # 1. Get Data
    new_data = fetch_data()

    # 2. Train AI & Process
    final_df = run_models(new_data)

    # 3. Save
    save_to_db(final_df)


if __name__ == "__main__":
    main_flow()
