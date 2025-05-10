import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import re
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime

class AmazonSponsoredScraper:
    def __init__(self, search_term, num_pages=3):
        self.search_term = search_term
        self.num_pages = num_pages
        self.base_url = "https://www.amazon.in"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'keep-alive',
            'Referer': 'https://www.amazon.in',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
        self.products = []
        
    def search_url(self, page=1):
        """Generate search URL for the given page"""
        return f"{self.base_url}/s?k={self.search_term.replace(' ', '+')}&page={page}"
    
    def get_page(self, url):
        """Fetch page content with retries"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=self.headers)
                if response.status_code == 200:
                    return response.text
                else:
                    print(f"Failed to get page, status code: {response.status_code}")
            except Exception as e:
                print(f"Error fetching page (attempt {attempt+1}/{max_retries}): {e}")
            
            if attempt < max_retries - 1:
                sleep_time = random.uniform(3, 7)
                print(f"Retrying in {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)
        
        return None
    
    def extract_sponsored_products(self, html_content):
        """Extract sponsored products from the page"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Look for sponsored product listings
        sponsored_products = []
        
        # Debug: Save HTML to file for inspection
        with open(f"amazon_page_debug_{int(time.time())}.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        
        # Search for products with sponsored tag
        product_cards = soup.select('div[data-component-type="s-search-result"]')
        print(f"Found {len(product_cards)} product cards in total")
        
        # Debug: look for sponsored labels
        all_sponsored_tags = soup.select('span.s-label-popover-default .a-color-secondary')
        print(f"Found {len(all_sponsored_tags)} sponsored tags")
        
        for card in product_cards:
            # Multiple ways to identify sponsored products - try different methods
            sponsored_tag = card.select_one('span.s-label-popover-default .a-color-secondary')
            sponsored_in_attrs = False
            
            # Check if "sponsored" appears in any data attributes
            for attr_name, attr_value in card.attrs.items():
                if isinstance(attr_value, str) and 'sponsor' in attr_value.lower():
                    sponsored_in_attrs = True
                    break
                    
            # Check for other potential sponsored indicators
            alt_sponsored_tag = card.select_one('.puis-sponsored-label-text')
            
            if (not sponsored_tag or 'Sponsored' not in sponsored_tag.get_text(strip=True)) and \
               not sponsored_in_attrs and not alt_sponsored_tag:
                continue
                
            try:
                # Extract product details
                title_element = card.select_one('h2 a.a-link-normal span')
                title = title_element.get_text(strip=True) if title_element else "N/A"
                
                # Get Product URL
                product_link_element = card.select_one('h2 a.a-link-normal')
                product_url = self.base_url + product_link_element.get('href') if product_link_element else "N/A"
                
                # Extract brand
                brand_element = card.select_one('.a-size-base.a-color-secondary')
                brand = brand_element.get_text(strip=True) if brand_element else "N/A"
                if brand == "N/A":
                    # Try alternate brand location
                    brand_element = card.select_one('h5 .a-size-base')
                    brand = brand_element.get_text(strip=True) if brand_element else "N/A"
                
                # Extract rating
                rating_element = card.select_one('i.a-icon-star-small span')
                rating_text = rating_element.get_text(strip=True) if rating_element else "N/A"
                rating = rating_text.split(' ')[0] if rating_text != "N/A" else "N/A"
                
                # Extract review count
                reviews_element = card.select_one('span.a-size-base.s-underline-text')
                reviews = reviews_element.get_text(strip=True) if reviews_element else "0"
                
                # Extract price
                price_element = card.select_one('.a-price-whole')
                price = price_element.get_text(strip=True) if price_element else "N/A"
                if price != "N/A":
                    price = "₹" + price
                
                # Extract image URL
                img_element = card.select_one('img.s-image')
                img_url = img_element.get('src') if img_element else "N/A"
                
                # Create product dictionary
                product = {
                    'product_title': title,
                    'brand': brand,
                    'rating': rating,
                    'num_reviews': reviews,
                    'selling_price': price,
                    'image_url': img_url,
                    'product_url': product_url
                }
                
                sponsored_products.append(product)
                
            except Exception as e:
                print(f"Error extracting product info: {e}")
                continue
            
        return sponsored_products
    
    def scrape(self):
        """Main scraping function to go through all pages"""
        all_products = []
        
        for page in range(1, self.num_pages + 1):
            print(f"Scraping page {page}...")
            url = self.search_url(page)
            html_content = self.get_page(url)
            
            if not html_content:
                print(f"Failed to get content for page {page}, skipping.")
                continue
                
            products = self.extract_sponsored_products(html_content)
            print(f"Found {len(products)} sponsored products on page {page}")
            all_products.extend(products)
            
            # Random sleep between page requests to avoid being blocked
            if page < self.num_pages:
                sleep_time = random.uniform(2, 5)
                print(f"Waiting {sleep_time:.2f} seconds before next page...")
                time.sleep(sleep_time)
        
        self.products = all_products
        return all_products
    
    def save_to_csv(self, filename='amazon_sponsored_products.csv'):
        """Save scraped products to CSV"""
        if not self.products:
            print("No products to save.")
            # Create empty DataFrame with proper columns to avoid errors
            empty_df = pd.DataFrame(columns=[
                'product_title', 'brand', 'rating', 'num_reviews', 
                'selling_price', 'image_url', 'product_url'
            ])
            empty_df.to_csv(filename, index=False)
            print(f"Created empty CSV file: {filename}")
            return filename
            
        df = pd.DataFrame(self.products)
        df.to_csv(filename, index=False)
        print(f"Saved {len(self.products)} products to {filename}")
        return filename

class DataCleaner:
    def __init__(self, filepath):
        self.filepath = filepath
        self.df = pd.read_csv(filepath)
        self.cleaned_filepath = None
        
    def clean(self):
        """Clean the data"""
        # Make a copy to avoid modifying original
        df = self.df.copy()
        
        # Remove duplicates
        original_count = len(df)
        df.drop_duplicates(subset=['product_title', 'brand'], inplace=True)
        print(f"Removed {original_count - len(df)} duplicate products")
        
        # Clean price column
        df['selling_price'] = df['selling_price'].apply(self._clean_price)
        
        # Clean ratings
        df['rating'] = df['rating'].apply(self._clean_rating)
        
        # Clean review count
        df['num_reviews'] = df['num_reviews'].apply(self._clean_reviews)
        
        # Clean brand
        df['brand'] = df['brand'].apply(lambda x: x.strip() if isinstance(x, str) else x)
        
        # Handle missing values
        for col in ['brand', 'product_title']:
            df[col] = df[col].fillna('Unknown')
            
        # Set the cleaned dataframe
        self.df = df
        return df
    
    def _clean_price(self, price):
        """Convert price string to numeric"""
        if isinstance(price, str):
            # Remove currency symbol, commas and spaces
            price = re.sub(r'[₹,\s]', '', price)
            try:
                return float(price)
            except ValueError:
                return None
        return price
    
    def _clean_rating(self, rating):
        """Convert rating string to numeric"""
        if isinstance(rating, str) and rating != "N/A":
            try:
                return float(rating.split(' ')[0])
            except (ValueError, IndexError):
                return None
        return None
    
    def _clean_reviews(self, reviews):
        """Convert review count to numeric"""
        if isinstance(reviews, str):
            # Remove commas and other non-numeric characters
            reviews = re.sub(r'[^\d]', '', reviews)
            if reviews:
                return int(reviews)
        return 0
    
    def save_cleaned_data(self, filename=None):
        """Save cleaned data to CSV"""
        if filename is None:
            base, ext = os.path.splitext(self.filepath)
            filename = f"{base}_cleaned{ext}"
        
        self.df.to_csv(filename, index=False)
        self.cleaned_filepath = filename
        print(f"Cleaned data saved to {filename}")
        return filename

class DataAnalyzer:
    def __init__(self, df):
        self.df = df
        self.output_dir = 'amazon_analysis_output'
        
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def brand_performance(self):
        """Analyze brand performance"""
        # Count products per brand
        brand_counts = self.df['brand'].value_counts()
        
        # Average rating by brand
        brand_ratings = self.df.groupby('brand')['rating'].mean().sort_values(ascending=False)
        
        # Create bar chart for top 5 brands by frequency
        plt.figure(figsize=(12, 6))
        ax = brand_counts.head(5).plot(kind='bar', color='skyblue')
        plt.title('Top 5 Brands by Number of Products', fontsize=16)
        plt.xlabel('Brand', fontsize=14)
        plt.ylabel('Number of Products', fontsize=14)
        plt.xticks(rotation=45, ha='right')
        
        # Add count labels on top of bars
        for i, v in enumerate(brand_counts.head(5)):
            ax.text(i, v + 0.1, str(v), ha='center', fontsize=12)
            
        plt.tight_layout()
        top_brands_chart = f"{self.output_dir}/top_brands_chart.png"
        plt.savefig(top_brands_chart)
        
        # Create pie chart for brand share
        plt.figure(figsize=(10, 10))
        # Combine smaller brands into "Others"
        top_n = 5
        other_count = brand_counts.iloc[top_n:].sum()
        pie_data = pd.concat([brand_counts.head(top_n), pd.Series({'Others': other_count})])
        
        plt.pie(pie_data, labels=pie_data.index, autopct='%1.1f%%', startangle=90, 
                shadow=True, explode=[0.05]*len(pie_data))
        plt.title('Brand Market Share', fontsize=16)
        plt.axis('equal')  # Equal aspect ratio ensures pie is circular
        plt.tight_layout()
        brand_share_chart = f"{self.output_dir}/brand_share_chart.png"
        plt.savefig(brand_share_chart)
        
        return {
            'brand_counts': brand_counts,
            'brand_ratings': brand_ratings,
            'top_brands_chart': top_brands_chart,
            'brand_share_chart': brand_share_chart
        }
    
    def price_vs_rating(self):
        """Analyze relationship between price and rating"""
        # Filter out products with missing ratings or prices
        valid_df = self.df.dropna(subset=['rating', 'selling_price'])
        
        # Create scatter plot
        plt.figure(figsize=(12, 8))
        plt.scatter(valid_df['rating'], valid_df['selling_price'], alpha=0.6)
        plt.title('Price vs Rating', fontsize=16)
        plt.xlabel('Rating', fontsize=14)
        plt.ylabel('Price (₹)', fontsize=14)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        price_rating_scatter = f"{self.output_dir}/price_rating_scatter.png"
        plt.savefig(price_rating_scatter)
        
        # Create rating bins
        valid_df['rating_bin'] = pd.cut(valid_df['rating'], 
                                       bins=[0, 3.0, 3.5, 4.0, 4.5, 5.0],
                                       labels=['0-3.0', '3.0-3.5', '3.5-4.0', '4.0-4.5', '4.5-5.0'])
        
        # Average price by rating range
        price_by_rating = valid_df.groupby('rating_bin')['selling_price'].mean().reset_index()
        
        plt.figure(figsize=(12, 6))
        ax = sns.barplot(x='rating_bin', y='selling_price', data=price_by_rating)
        plt.title('Average Price by Rating Range', fontsize=16)
        plt.xlabel('Rating Range', fontsize=14)
        plt.ylabel('Average Price (₹)', fontsize=14)
        
        # Add average price labels on top of bars
        for i, row in enumerate(price_by_rating.itertuples()):
            ax.text(i, row.selling_price + 10, f'₹{row.selling_price:.2f}', 
                    ha='center', fontsize=12)
        
        plt.tight_layout()
        price_by_rating_chart = f"{self.output_dir}/price_by_rating_chart.png"
        plt.savefig(price_by_rating_chart)
        
        # Identify high-rated + low-price products (value for money)
        # High rating: >= 4.0, Low price: below median price
        median_price = valid_df['selling_price'].median()
        value_products = valid_df[(valid_df['rating'] >= 4.0) & 
                                 (valid_df['selling_price'] < median_price)]
        value_products = value_products.sort_values('rating', ascending=False)
        
        return {
            'price_rating_scatter': price_rating_scatter,
            'price_by_rating_chart': price_by_rating_chart,
            'value_products': value_products.head(10)  # Top 10 value products
        }
    
    def review_rating_distribution(self):
        """Analyze review count and rating distribution"""
        # Top products by number of reviews
        top_reviewed = self.df.sort_values('num_reviews', ascending=False).head(5)
        
        plt.figure(figsize=(14, 6))
        ax = sns.barplot(x='product_title', y='num_reviews', data=top_reviewed)
        plt.title('Top 5 Products by Number of Reviews', fontsize=16)
        plt.xlabel('Product', fontsize=14)
        plt.ylabel('Number of Reviews', fontsize=14)
        plt.xticks(rotation=45, ha='right')
        
        # Add review count labels
        for i, v in enumerate(top_reviewed['num_reviews']):
            ax.text(i, v + 10, str(v), ha='center', fontsize=12)
            
        plt.tight_layout()
        top_reviews_chart = f"{self.output_dir}/top_reviews_chart.png"
        plt.savefig(top_reviews_chart)
        
        # Top products by rating (with at least 10 reviews)
        min_reviews = 10
        #top_rated = self.df[self.df['num_reviews'] >= min_reviews].sort_values('rating', ascending=False).head(5)
        top_rated = self.df[(self.df['num_reviews'] >= min_reviews) & (self.df['rating'].notnull())].sort_values('rating', ascending=False).head(5)

        plt.figure(figsize=(14, 6))
        ax = sns.barplot(x='product_title', y='rating', data=top_rated)
        plt.title(f'Top 5 Highest Rated Products (with at least {min_reviews} reviews)', fontsize=16)
        plt.xlabel('Product', fontsize=14)
        plt.ylabel('Rating', fontsize=14)
        plt.xticks(rotation=45, ha='right')
        plt.ylim(0, 5.5)  # Rating scale is 0-5
        
        # Add rating labels
        for i, v in enumerate(top_rated['rating']):
            ax.text(i, v + 0.1, f"{v:.1f}", ha='center', fontsize=12)
            
        plt.tight_layout()
        top_rated_chart = f"{self.output_dir}/top_rated_chart.png"
        plt.savefig(top_rated_chart)
        
        return {
            'top_reviews_chart': top_reviews_chart,
            'top_rated_chart': top_rated_chart,
            'top_reviewed': top_reviewed,
            'top_rated': top_rated
        }
    
    def generate_report(self, title="Amazon Sponsored Products Analysis"):
        """Generate a report with all analyses"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report_file = f"{self.output_dir}/amazon_analysis_report.md"
        
        with open(report_file, 'w',encoding="utf-8") as f:
            # Header
            f.write(f"# {title}\n\n")
            f.write(f"*Generated on: {timestamp}*\n\n")
            f.write(f"*Total Products Analyzed: {len(self.df)}*\n\n")
            
            # Brand Performance
            f.write("## 1. Brand Performance Analysis\n\n")
            brand_results = self.brand_performance()
            
            f.write("### Top Brands by Number of Products\n\n")
            f.write("![Top Brands](./top_brands_chart.png)\n\n")
            f.write("**Key Insights:**\n")
            f.write("- The market is dominated by " + brand_results['brand_counts'].index[0] + "\n")
            f.write("- Top 5 brands account for " + 
                   f"{100 * brand_results['brand_counts'].head(5).sum() / brand_results['brand_counts'].sum():.1f}% " + 
                   "of the sponsored products\n\n")
            
            f.write("### Brand Market Share\n\n")
            f.write("![Brand Share](./brand_share_chart.png)\n\n")
            
            f.write("### Average Rating by Brand (Top 10)\n\n")
            f.write("| Brand | Average Rating |\n")
            f.write("|-------|---------------|\n")
            for brand, rating in brand_results['brand_ratings'].head(10).items():
                f.write(f"| {brand} | {rating:.2f} |\n")
            f.write("\n")
            
            # Price vs Rating
            f.write("## 2. Price vs Rating Analysis\n\n")
            price_rating_results = self.price_vs_rating()
            
            f.write("### Price vs Rating Scatter Plot\n\n")
            f.write("![Price vs Rating](./price_rating_scatter.png)\n\n")
            f.write("**Key Insights:**\n")
            f.write("- There's a wide range of prices across different rating levels\n")
            f.write("- Most highly-rated products (4.5+) are distributed across various price points\n\n")
            
            f.write("### Average Price by Rating Range\n\n")
            f.write("![Price by Rating](./price_by_rating_chart.png)\n\n")
            
            f.write("### Value for Money Products (High Rating, Low Price)\n\n")
            f.write("| Product | Brand | Rating | Price (₹) | Reviews |\n")
            f.write("|---------|-------|--------|-----------|--------|\n")
            for _, product in price_rating_results['value_products'].iterrows():
                f.write(f"| {product['product_title'][:50]}... | {product['brand']} | {product['rating']:.1f} | {product['selling_price']:.2f} | {product['num_reviews']} |\n")
            f.write("\n")
            
            # Review & Rating Distribution
            f.write("## 3. Reviews and Ratings Analysis\n\n")
            review_results = self.review_rating_distribution()
            
            f.write("### Top Products by Number of Reviews\n\n")
            f.write("![Top Reviewed](./top_reviews_chart.png)\n\n")
            f.write("**Key Insights:**\n")
            f.write("- The most reviewed product has significantly more reviews than others\n")
            f.write("- Products with high review counts indicate popular items with established market presence\n\n")
            
            f.write("### Top Rated Products\n\n")
            f.write("![Top Rated](./top_rated_chart.png)\n\n")
            f.write("**Key Insights:**\n")
            f.write("- Top rated products maintain exceptional customer satisfaction\n")
            f.write("- Several products achieve near-perfect ratings despite having multiple reviews\n\n")
            
            # Summary
            f.write("## 4. Summary and Recommendations\n\n")
            f.write("**Market Insights:**\n")
            f.write("- The sponsored soft toys market appears to be dominated by a few key brands\n")
            f.write("- There are several high-quality options (high ratings) available at various price points\n")
            f.write("- Products with high review counts and high ratings represent established market leaders\n\n")
            
            f.write("**Recommendations:**\n")
            f.write("- For value-conscious consumers, focus on the 'Value for Money' products section\n")
            f.write("- For gift-giving, consider the top-rated products with substantial review counts\n")
            f.write("- For brand loyalty and consistency, " + brand_results['brand_counts'].index[0] + 
                   " offers the widest selection of sponsored products\n\n")
            
            f.write("---\n")
            f.write("*This report was auto-generated based on scraped Amazon.in data*\n")
        
        return report_file

def main():
    # 1. Scraping
    search_term = "soft toys"
    print(f"Starting Amazon sponsored product scraper for '{search_term}'...")
    scraper = AmazonSponsoredScraper(search_term, num_pages=3)
    scraper.scrape()
    raw_csv = scraper.save_to_csv()
    
    # 2. Cleaning
    print("\nCleaning the scraped data...")
    cleaner = DataCleaner(raw_csv)
    cleaned_df = cleaner.clean()
    cleaned_csv = cleaner.save_cleaned_data()
    
    # Check if we have any data
    if cleaned_df.empty:
        print("\nNo sponsored products were found. This could be due to:")
        print("1. Amazon might be blocking scraping attempts")
        print("2. The HTML structure might have changed")
        print("3. There might genuinely be no sponsored products for this search")
        print("\nTry the following:")
        print("- Use a VPN or proxy")
        print("- Add more randomized delays between requests")
        print("- Update the HTML selectors in the code")
        return
    
    # 3. Analysis
    print("\nPerforming data analysis and visualization...")
    analyzer = DataAnalyzer(cleaned_df)
    report_file = analyzer.generate_report()
    
    print(f"\nComplete! Analysis report saved to {report_file}")
    print("You can find all visualizations in the 'amazon_analysis_output' directory")

if __name__ == "__main__":
    main()