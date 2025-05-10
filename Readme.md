# 🧸 Amazon Soft Toys Data Scraping & Analysis

This project involves scraping **sponsored products** for **"soft toys"** from Amazon.in and performing detailed data cleaning, analysis, and visualization. The insights will help understand brand performance, pricing trends, rating distributions, and identify value-for-money products.

---

## 📌 Project Structure

### ✅ Part 1: Web Scraping

- **Target Website:** [Amazon.in](https://www.amazon.in)
- **Search Keyword:** `soft toys`
- **Pages Scraped:** First 2–3 pages
- **Focus:** Only Sponsored Products
- **Fields Extracted:**
  - Product Title
  - Brand
  - Number of Reviews
  - Rating (out of 5)
  - Selling Price
  - Image URL
  - Product URL
- **Output:** `raw_soft_toys_data.csv`

---

### ✅ Part 2: Data Cleaning

- Removed duplicate entries
- Converted prices to numeric format (₹ symbol and commas removed)
- Converted review counts and ratings to numeric data types
- Handled missing or inconsistent values
- **Output:** `cleaned_soft_toys_data.csv`

---

### ✅ Part 3: Analysis & Visualization

#### 📈 Brand Performance
- Count of products per brand
- Average rating by brand
- **Visualizations:**
  - Bar Chart: Top 5 Brands by Frequency
  - Pie Chart: Brand Share Percentage

#### 💸 Price vs Rating
- Scatter Plot: Price vs Rating
- Bar Chart: Average Price by Rating Range
- Identified High-Rated + Low-Priced Products (Value for Money)

#### ⭐ Review & Rating Distribution
- Bar Chart: Top 5 Products by Number of Reviews
- Bar Chart: Top 5 Products by Rating

---

## 📦 Final Deliverables

- `cleaned_soft_toys_data.csv` — Cleaned dataset
- `soft_toys_analysis.ipynb` (or `.pdf`) — Jupyter Notebook with:
  - Data cleaning steps
  - All visualizations
  - Bullet-point insights under each chart

---

## 🛠️ Tools & Libraries Used

- Python (Jupyter Notebook)
- `requests`, `BeautifulSoup` — For scraping
- `pandas`, `numpy` — For data manipulation
- `matplotlib`, `seaborn` — For visualization

---

## ⚠️ Disclaimer

This project is for **educational and research purposes only**. Scraping Amazon may violate their Terms of Service. Use responsibly.

---

## 📬 Contact

For queries or collaborations, feel free to reach out.

