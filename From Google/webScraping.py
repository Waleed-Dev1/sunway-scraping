from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pandas as pd
import time
import re
from loguru import logger

def setup_driver():
    """Set up and return a configured Chrome WebDriver."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode (no UI)
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-notifications")
    
    # Initialize the Chrome driver
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def get_shop_details(stores):
    """Visit each shop page and extract detailed information."""
    driver = setup_driver()
    detailed_data = []
    # stores = pd.read_csv("sunway_pyramid_shops.csv")
    
    for _, store in stores.iterrows():

        shop_url = store.get("url", "")
        if not shop_url:
            continue  # Skip if URL is missing

        try:
            driver.get(shop_url)
            
            # Wait for the shop page to load
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".logocontainer-shopview"))
            )
            
            # Extract shop details
            try:
                logo_element = driver.find_element(By.CSS_SELECTOR, ".logocontainer-shopview img")
                logo = logo_element.get_attribute("src")
            except:
                logo = "N/A"
            
            # Extract shop category
            try:
                category = driver.find_element(By.CSS_SELECTOR, ".__rounded-pill").text.strip()
            except:
                category = "N/A"
                
            # Extract shop description
            try:
                description = driver.find_element(By.CSS_SELECTOR, ".font-normal.long-shop-text-scroll").text.strip()
            except:
                description = "N/A"
                
            # Extract location
            try:
                location = driver.find_element(By.XPATH, "//a[@href='#mapZone']").text.strip()
            except:
                location = "N/A"

            detailed_data.append({
                "name": store["name"],
                "img":store["img"],
                "url": shop_url,
                "logo": logo,
                "category": category,
                "description": description,
                "location": location
            })
            
        except Exception as e:
            logger.error(f"Error scraping details from {shop_url}: {e}")
    
    driver.quit()
    
    # Create DataFrame and save to CSV
    if detailed_data:
        detailed_df = pd.DataFrame(detailed_data)
        detailed_df.to_csv("sunway_pyramid_shop_details.csv", index=False)
        return detailed_df
    
    return None




def scrape_sunway_pyramid_directory():
    """Scrape the Sunway Pyramid mall directory."""
    url = "https://www.sunwaypyramid.com/directory"
    driver = setup_driver()
    
    try:
        logger.info("Accessing the Sunway Pyramid directory...")
        driver.get(url)
        
        # Wait for the page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".btn-outline-danger"))
        )

        # Allow some time for initial content to load
        time.sleep(3)

        # Click "Load More" until it disappears
        while True:
            try:
                # Find all buttons with class ".btn-outline-danger"
                buttons = driver.find_elements(By.CSS_SELECTOR, ".btn-outline-danger")
                
                # Click only the button that contains "Load More"
                load_more_clicked = False
                for button in buttons:
                    if "Load More" in button.text:
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)  # Scroll into view
                        time.sleep(1)  # Allow time for scrolling
                        button.click()
                        time.sleep(2)  # Wait for new items to load
                        load_more_clicked = True
                        break  # Stop looking for other buttons once clicked
                
                # If no button was clicked, exit loop
                if not load_more_clicked:
                    logger.info("No more 'Load More' button. All items loaded.")
                    break  

            except Exception as e:
                logger.error(f"Error clicking 'Load More': {e}")
                break  # Exit loop if an error occurs


        # Extract all shop elements
        shop_data = []
        cards = driver.find_elements(By.CSS_SELECTOR, ".card")

        for card in cards:
            try:
                # Extract shop name
                title = card.find_element(By.CSS_SELECTOR, '.text-truncate').text.strip()
                directory_route=card.find_element(By.TAG_NAME, 'a').get_attribute("href")
                # Extract image URL
                img_url = card.find_element(By.TAG_NAME, 'img').get_attribute("src")

                # Append to list
                shop_data.append({"name": title, "img": img_url, "url":directory_route})
            except Exception as e:
                logger.error(f"Error processing card: {e}")

        # Convert to DataFrame and save as CSV
        df = pd.DataFrame(shop_data)
        # df.to_csv("sunway_pyramid_shops.csv", index=False)
        logger.info(f"Successfully scraped {len(shop_data)} shops from Sunway Pyramid directory.")

        get_shop_details(df)
    

    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        driver.quit()
