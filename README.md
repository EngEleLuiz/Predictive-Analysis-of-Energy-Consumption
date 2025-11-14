# ⚡ Energy Load Forecasting and Anomaly Detection Pipeline

This project implements an end-to-end data pipeline to forecast energy consumption (kWh) and detect real-time anomalies. It ingests data from public APIs, processes it, trains models, and serves the results to a dashboard.

---

## Overview

This system transitions a static data analysis script into a fully automated, production-ready data product. It addresses the domain of **Energy Management** by providing two key data science components:

1.  **Forecasting:** Predicts the energy demand for the next 24 hours using a time-series model.
2.  **Anomaly Detection:** Identifies unusual consumption patterns (e.g., high-demand spikes at off-peak hours) that deviate from the norm.

## 🏛️ Project Architecture & Tech Stack

The pipeline is built with a modern data stack, separating data engineering (DE) and data science (IDS) concerns.



* **Data Ingestion:** A Python script fetches data from a public API (e.g., a national grid operator like ONS or a weather API, as climate heavily influences demand).
* **Storage:** **PostgreSQL** is used as the data warehouse. It stores raw ingested data, cleaned/transformed data, and the final model outputs (predictions and anomalies).
* **Pipeline & Orchestration:** **Prefect** is used to schedule and manage the entire ETLT (Extract, Transform, Load, Train) process. The pipeline is scheduled to run daily (e.g., at midnight) to fetch new data and retrain models.
* **Data Science Models:**
    * **Forecasting:** A **Prophet** or **SARIMA** model is trained on historical data to predict future demand.
    * **Anomaly Detection:** An **Isolation Forest** algorithm identifies data points that are "unusual" based on historical patterns.
* **Serving & Visualization:** The final predictions and flagged anomalies are written back to the PostgreSQL database. A dashboard built in **Streamlit** (or **Power BI**) reads from this database to display the "network status" in near real-time.

---

## 🚀 Getting Started

### Prerequisites

* Python 3.9+
* Git
* A running PostgreSQL server
* Prefect Cloud account (optional, but recommended)

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
    cd your-repo-name
    ```

2.  **Create a virtual environment and activate it:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure your credentials:**
    * Rename the `config/config.example.ini` to `config/config.ini`.
    * Add your API keys and PostgreSQL database connection details to `config/config.ini`. (This file is ignored by Git to keep your secrets safe).

5.  **Set up the database:**
    * Run the `setup_db.sql` script on your PostgreSQL server to create the necessary tables.
    * `psql -U your_user -d your_db -f scripts/setup_db.sql`

### Running the Pipeline

1.  **Run the main Prefect flow:**
    This will register and execute the pipeline that ingests, processes, and models the data.
    ```bash
    python src/pipeline/main_flow.py
    ```

2.  **Start the Streamlit dashboard:**
    ```bash
    streamlit run src/visualization/app.py
    ```

---

## License

Distributed under the MIT License. See `LICENSE` for more information.
