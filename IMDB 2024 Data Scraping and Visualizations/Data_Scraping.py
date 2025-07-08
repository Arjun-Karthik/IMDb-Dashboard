#Importing Libraries
import os
import time
import glob
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

#Path of Cromedriver
path = "C:/Users/workstation/Downloads/chromedriver-win64/chromedriver.exe"
service = Service(executable_path=path)
options = Options()
driver = webdriver.Chrome(service=service, options=options)

#Website URL
website = "https://www.imdb.com/search/title/?title_type=feature&release_date=2024-01-01,2024-12-31&genres={genre}&sort=alpha,asc"
wait = WebDriverWait(driver, 10)

genres = [
    'action', 'adventure', 'animation', 'biography', 'comedy', 'crime',
    'documentary', 'drama', 'family', 'fantasy', 'history',
    'horror', 'music', 'musical', 'mystery', 'romance', 'sci-fi',
    'sport', 'thriller', 'war', 'western'
]

def clean_text(text):
    return text.strip().replace('\n', '').replace(',', '').replace('(', '').replace(')', '').lstrip('-')

def load_all_movies():
    total_loaded = 0
    while True:
        try:
            # Scroll down to the button using JavaScript
            load_more_btn = wait.until(EC.presence_of_element_located((By.XPATH, '//button[@class="ipc-btn ipc-btn--single-padding ipc-btn--center-align-content ipc-btn--default-height ipc-btn--core-base ipc-btn--theme-base ipc-btn--button-radius ipc-btn--on-accent2 ipc-text-button ipc-see-more__button"]')))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", load_more_btn)
            time.sleep(1)  # wait for scroll animation
        
            driver.execute_script("arguments[0].click();", load_more_btn)
            total_loaded += 50
            print(f"'Load more' clicked... ({total_loaded} movies loaded)")
            time.sleep(2)  # give time to load content
    
        except TimeoutException:
            print("No more '50 more' button found.")
            break

def clean_runtime(runtime_str):
    if pd.isna(runtime_str) or runtime_str == 'Unknown':
        return None
    
    runtime_str = str(runtime_str).lower().strip()

    if 'h' in runtime_str:
        hours = re.search(r'(\d+)h', runtime_str)
        minutes = re.search(r'(\d+)m', runtime_str)
        total_minutes = 0
        if hours:
            total_minutes += int(hours.group(1)) * 60
        if minutes:
            total_minutes += int(minutes.group(1))
        return total_minutes
    
    elif ':' in runtime_str:
        parts = runtime_str.split(':')
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            return int(parts[0]) * 60 + int(parts[1])
    
    elif runtime_str.replace('min', '').strip().isdigit():
        return int(runtime_str.replace('min', '').strip())

    return None

def scrape_genre(genre):
    print(f"Scraping genre: {genre}")
    url = website.format(genre=genre)
    driver.get(url)
    time.sleep(3)

    load_all_movies()

    movie_blocks = driver.find_elements(By.XPATH, '//div[@class = "sc-86fea7d1-0 kFfAkw"]')
            
    data = []
                
    for block in movie_blocks:
        title = ratings = vote_counts = runtime = "N/A"
        
        try:
            raw_title = block.find_element(By.XPATH, './div/a/h3').text
            title = raw_title.split('. ', 1)[1] if '. ' in raw_title else raw_title
        except:
            pass
            
        try:
            ratings = block.find_element(By.XPATH, './/div[@data-testid = "ratingGroup--container"]/span/span[1]').text
        except:
            pass
        try:
            vote_counts = block.find_element(By.XPATH, './/div[@data-testid = "ratingGroup--container"]/span/span[2]').text
            vote_counts = clean_text(vote_counts)
        except:
            pass
        try:
            runtime = block.find_element(By.XPATH, './div/span[2]').text      
        except:
            pass

        data.append({'Title' : title, 'Genre' : genre, 'Ratings' : ratings, 'Vote_Counts' : vote_counts, 'Runtime' : runtime})

    # Create and clean DataFrame
    df = pd.DataFrame(data)

    # Convert runtime to cleaned minutes
    df['Runtime'] = df['Runtime'].apply(clean_runtime)

    #Change to numeric Datatype
    df['Ratings'] = pd.to_numeric(df['Ratings'], errors='coerce').round(1)
    df['Vote_Counts'] = df['Vote_Counts'].str.replace('[^0-9]', '', regex=True)  # Remove non-digit chars
    df['Vote_Counts'] = pd.to_numeric(df['Vote_Counts'], errors='coerce')
    df['Runtime'] = pd.to_numeric(df['Runtime'], errors='coerce')

    # Fill missing values
    df['Ratings'] = df['Ratings'].fillna(df['Ratings'].median()).round(1)
    df['Vote_Counts'] = df['Vote_Counts'].fillna(df['Vote_Counts'].median())
    df['Runtime'] = df['Runtime'].fillna(df['Runtime'].median())

    df['Vote_Counts'] = df['Vote_Counts'].astype(int)
    df['Runtime'] = df['Runtime'].astype(int)

    df = df.drop_duplicates()

    #Save to CSV
    output_dir = "imdb_data"
    os.makedirs(output_dir, exist_ok=True)
    filename = f"genre_{genre}.csv"
    filepath = os.path.join(output_dir, filename)
    df.to_csv(filepath, index=False, encoding='utf-8-sig')
    print(f"Saved {len(df)} movies to {filepath}")

#Scraping Data    
for genre in genres:
    try:
        scrape_genre(genre)
    except Exception as e:
        print(f"Error scraping {genre}: {e}")
        continue

driver.quit()
print("Scraping complete")

#Merging CSV files
files = glob.glob("C:/Users/workstation/Downloads/Data_Scraping_and_Visualization/imdb_data/genre_*")
merged_csv = pd.concat([pd.read_csv(file, usecols = ['Title', 'Genre', 'Ratings', 'Vote_Counts', 'Runtime']) for file in files])
merged_csv.to_csv('IMDB_Movies_Data.csv', index=False, encoding='utf-8-sig')
print(f'{len(files)} csv files merged')