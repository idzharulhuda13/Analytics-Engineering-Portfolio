# 🤖 Analytics Engineering Portfolio

Welcome to my **Analytics Engineering & Data Science Portfolio**. This project showcases an end-to-end data application built with **Streamlit**, **DuckDB**, and **Plotly**, designed to provide interactive insights through specialized dashboards.

---

## 🌟 Overview

This repository features my professional journey and technical expertise, presented as a high-performance web application. It integrates several data-driven modules:

- **💼 Professional Portfolio:** An interactive resume powered by an in-memory DuckDB database, detailing my experience as an Analytics Engineer, AI Engineer, and Data Analyst.
- **📊 Student Performance Dashboard:** Deep-dive analysis into educational datasets, exploring demographics, test preparations, and socioeconomic impacts on student scores.
- **🚗 BMW Global Sales Dashboard:** A comprehensive market analysis of automotive sales from 2018–2025, featuring regional trends, model performance, and EV transition metrics.

---

## 🛠️ Tech Stack

- **Framework:** [Streamlit](https://streamlit.io/) (Web UI & Interactivity)
- **Database:** [DuckDB](https://duckdb.org/) (In-memory analytical processing)
- **Data Handling:** [Pandas](https://pandas.pydata.org/)
- **Visualization:** [Plotly](https://plotly.com/python/) (Dynamic & responsive charts)
- **Styling:** Custom CSS with Glassmorphism and Premium Aesthetics

---

## 📂 Project Structure

```text
.
├── Resume.py                # Main application entry point (Portfolio/Bio)
├── data/                    # Raw datasets (CSV)
│   ├── StudentsPerformance.csv
│   └── bmw_global_sales_2018_2025.csv
├── pages/                   # Multi-page dashboard modules
│   ├── 1_Student_Performance.py
│   └── 2_BMW_Global_Sales.py
├── .streamlit/              # Streamlit configuration
├── pyproject.toml           # Dependency management (uv)
└── requirements.txt         # Standard pip dependencies
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) (recommended) or `pip`

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/idzharulhuda13/Analytics-Engineering-Portfolio.git
   cd Analytics-Engineering-Portfolio
   ```

2. **Install dependencies:**
   Using `uv`:
   ```bash
   uv sync
   ```
   Or using `pip`:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   streamlit run Resume.py
   ```

---

## 🛡️ Data & Privacy

This portfolio uses DuckDB for fast, secure, and ephemeral data processing. No personal data is stored outside the localized session, ensuring a clean and performant user experience.

---

## ✉️ Contact

**Idzharul Huda**
- 📍 Jakarta, Indonesia
- 📧 [Contact me via Email](mailto:idzharul.huda@gmail.com)
- 🔗 [LinkedIn](https://linkedin.com/in/idzharulhuda)
- 🐙 [GitHub](https://github.com/idzharulhuda13)

---

Built with ❤️ by Idzharul Huda
