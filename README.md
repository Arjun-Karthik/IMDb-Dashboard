# IMDB_2024_Data_Scraping_and_Visualizations

## ⚙️ Workflow
1. Data Scraping

Uses Selenium to scrape movie title, genre, rating, vote counts, and runtime from IMDb.

Scraped data is stored in IMDB_Movies_Data.csv.

Genre strings are already merged into a single column (e.g., "Action, Drama").

2. Data Cleaning

Converts votes and runtime columns to numeric values.

Removes duplicates and handles missing data.

Merges genre lists during scraping itself to avoid duplication.

3. Streamlit Dashboard

Upload IMDB_Movies_Data.csv in the app.

Apply filters (genre, rating, vote count, duration).

Explore:

Top 10 rated movies

Genre-wise stats

Rating distribution

Correlation between ratings and votes

Download filtered data

## ▶️ Running the App
Ensure Python 3.8+ is installed.

1. Clone the repo:

git clone https://github.com/yourusername/IMDb_Dashboard_Project.git
cd IMDb_Dashboard_Project

2.Install dependencies

pip install -r requirements.txt

3. Run Streamlit app

streamlit run app.py

4. Upload the CSV file (IMDB_Movies_Data.csv) when prompted in the app.

## 🧩 Features

Genre-based filtering with exploded multi-genre support.

Correlation and distribution plots using Plotly.

Download filtered dataset as CSV.

Genre-wise average ratings and vote counts.

Rating-based leaderboards and extremes.

## ✅ Requirements

streamlit

selenium

pandas

plotly

matplotlib

seaborn

Install all with:

pip install -r requirements.txt

## 📸 Screenshots

### 📊 Genre Distribution

<img src="screenshots/barchart.png" width="800"/>

### 📊 Distribution of Movie Ratings

<img src="screenshots/histogram.png" width="800"/>

## 📃 License

This project is licensed under the MIT License – see the LICENSE file for details.

