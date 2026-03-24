# 🤖 Analytics Engineering Portfolio

Welcome to my **Analytics Engineering & Data Science Portfolio**. This project showcases an end-to-end data application built with **dbt**, **DuckDB**, and **Streamlit**, designed to provide interactive insights through specialized dashboards.

---

## 🌟 Overview

This repository features my professional journey and technical expertise, presented as a high-performance web application. It integrates several data-driven modules:

- **💼 Professional Portfolio:** An interactive resume powered by an in-memory DuckDB database, detailing my experience as an Analytics Engineer, AI Engineer, and Data Analyst.
- **🍫 Chocolate Sales Datamart:** A professional dbt project featuring a robust **src -> dim -> mrt** architecture, processing raw parquet data into enriched analytical tables.

---

## 🛠️ Tech Stack

- **Modeling:** [dbt](https://www.getdbt.com/) (Data transformations & lineage)
- **Database:** [DuckDB](https://duckdb.org/) (In-memory analytical processing)
- **Storage:** [Parquet](https://parquet.apache.org/) (Highly optimized columnar storage)
- **Framework:** [Streamlit](https://streamlit.io/) (Web UI & Interactivity)
- **Visualization:** [Altair](https://altair-viz.github.io/) (Declarative statistical visualization)
- **Environment:** [uv](https://github.com/astral-sh/uv) (Fast Python dependency management)

---

## 📂 Project Structure

```text
.
├── Resume.py                # Main application entry point (Portfolio/Bio)
├── dbt_models/              # dbt Architecture
│   ├── src/                 # Staging layer (Raw parquet sources)
│   ├── dim/                 # Dimension layer (Enriched business logic)
│   └── mrt/                 # Mart layer (Final analytics-ready tables)
├── data/                    # Optimized source data
├── pages/                   # Multi-page dashboard modules (Coming soon)
├── .streamlit/              # Streamlit configuration
├── .vscode/                 # Pre-configured dbt Power User settings
├── dbt_project.yml          # dbt configuration
└── pyproject.toml           # Dependency management (uv)
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) (recommended)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/idzharulhuda13/Analytics-Engineering-Portfolio.git
   cd Analytics-Engineering-Portfolio
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   ```

### Running the Data Pipeline (dbt)

To rebuild the analytical models from raw parquet data:
```bash
uv run dbt run --profiles-dir .
```

### Running the Web Application

To launch the interactive Streamlit dashboard:
```bash
uv run streamlit run Resume.py
```

---

## 🛡️ Data Engineering Best Practices

This project implements modern data stack principles:
- **Columnar Efficiency**: Raw CSVs were converted to **Parquet**, reducing storage size by **>70%** and improving DuckDB query performance.
- **Dimensional Modeling**: Implemented a staged dbt architecture to ensure data quality and reusable business logic.
- **Environment Isolation**: Uses `uv` for reproducible, isolated Python environments.

---

## ✉️ Contact

**Idzharul Huda**
- 📍 Jakarta, Indonesia
- 📧 [Contact me via Email](mailto:idzharul.huda@gmail.com)
- 🔗 [LinkedIn](https://linkedin.com/in/idzharulhuda)
- 🐙 [GitHub](https://github.com/idzharulhuda13)

---

Built with ❤️ by Idzharul Huda
