# Predictive-Analysis-of-Energy-Consumption
# End-to-End Energy Consumption Analysis Pipeline

![Power BI Dashboard Screenshot](httpsGET_A_SCREENSHOT_OF_YOUR_DASHBOARD_AND_LINK_IT_HERE.png) to be added

## 1. Project Overview

This project demonstrates a complete, end-to-end data engineering pipeline. It ingests raw, time-series data from 2 million+ household energy consumption readings, processes it through a robust ETL workflow, stores it in a relational database, performs predictive modeling, and presents the findings in an interactive business intelligence dashboard.

This repository serves as a practical demonstration of skills in data ingestion, transformation, storage, and analysis, combining my background in Electrical Engineering with a specialization in Data Engineering.

## 2. Tech Stack & Architecture

This pipeline is built using a modern data stack, demonstrating proficiency in each component of the data lifecycle.

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Data Ingestion** | **Python** (`requests`, `zipfile`) | Fetch & extract the raw dataset. |
| **ETL/Transformation** | **Python** (`Pandas`) | Clean, transform, and perform feature engineering. |
| **Database Storage** | **PostgreSQL** | Store raw and processed data as the single source of truth. |
| **ML Modeling** | **Python** (`Scikit-learn`) | Train a regression model to forecast future consumption. |
| **Data Visualization** | **Power BI** | Create an interactive dashboard connected directly to the DB. |

### Pipeline Architecture
[UCI Data (Raw .txt)] -> [Python Ingest Script] -> [PostgreSQL: "raw_data" table] | V [PostgreSQL: "raw_data" table] -> [Python Transform Script] -> [PostgreSQL: "clean_hourly_data" & "feature_table"] | V [PostgreSQL: "feature_table"] -> [Python Model Script] -> [PostgreSQL: "predictions_table"] | V [PostgreSQL Database] <--- (DirectQuery) ---> [Power BI Dashboard]

## 3. Project Features

### Data Ingestion (`ingestion.py`)
* Downloads the 20MB zipped dataset from the UCI repository.
* Extracts the `.txt` file.
* Uses `sqlalchemy` to connect to a PostgreSQL database.
* Ingests the 2.07 million rows in efficient chunks (`chunksize=10000`) into a "raw" data table.

### ETL & Transformation (`transform.py`)
* **Data Cleaning:**
    * Handles missing values (`?`) using time-series appropriate methods (forward-fill).
    * Parses and combines `Date` and `Time` columns into a single `timestamp` (index).
    * Corrects all data types for numeric analysis.
* **Feature Engineering (The Electrical Engineering Edge):**
    * Creates a `total_sub_metering` column.
    * Calculates **`unaccounted_power`** (`Global_active_power` - `Total_sub_metering`), identifying energy used by other non-metered sources.
* **Data Aggregation:**
    * Resamples the per-minute data into **hourly averages** to create a clean, aggregated table (`hourly_consumption`) for BI analysis.

### Predictive Modeling (`model.py`)
* Uses the aggregated hourly data to forecast future energy consumption.
* **Feature Creation:** Generates time-lag features (e.g., `consumption_24h_ago`) and time-based features (`hour`, `day_of_week`, `is_weekend`).
* **Model:** Implements a `RandomForestRegressor` (or similar) from `Scikit-learn` to predict `global_active_power`.
* **Output:** Saves predictions to a new table (`predictions`) for visualization in the dashboard.

### BI Dashboard (Power BI)
* Connects **directly** to the PostgreSQL database (using DirectQuery or Import mode).
* **Page 1 (Overview):** KPIs for total consumption, average voltage, and peak demand periods.
* **Page 2 (Deep Dive):** Analysis of sub-metering (Kitchen vs. Laundry) and the `unaccounted_power` feature.
* **Page 3 (Forecast):** A line chart overlaying **Actual Consumption** vs. **Predicted Consumption** from the ML model.

## 4. Key Insights (Examples)

* **Peak Consumption:** Identified that peak energy usage consistently occurs on Saturdays between 8 PM and 9 PM.
* **Unaccounted Power:** The `unaccounted_power` feature revealed that an average of **18%** of all energy consumption is not captured by the primary sub-meters, likely due to large appliances like HVAC or water heaters.
* **Weekend vs. Weekday:** A clear pattern emerges where `sub_metering_3` (laundry/water-heater) usage is 40% higher on weekends.

## 5. How to Run This Project

### Prerequisites
* Python 3.9+
* PostgreSQL Server (running locally or on a server)
* Power BI Desktop

### 1. Clone the Repository
```bash
git clone [https://github.com/](https://github.com/)[YOUR_USERNAME]/[YOUR_REPO_NAME].git
cd [YOUR_REPO_NAME]
