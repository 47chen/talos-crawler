import time
import random
import csv
import os
from datetime import datetime
from collections import OrderedDict
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException

def setup_driver():
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')
    options.add_argument('--width=1980')
    options.add_argument('--height=1080')
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/109.0",
        "Mozilla/5.0 (X11; Linux i686; rv:109.0) Gecko/20100101 Firefox/109.0",
        "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/109.0",
        "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:109.0) Gecko/20100101 Firefox/109.0",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/109.0",
        "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/109.0",
    ]
    
    # Randomly select a user agent
    options.set_preference("general.useragent.override", random.choice(user_agents))
    
    service = FirefoxService(GeckoDriverManager().install())
    return webdriver.Firefox(service=service, options=options)

def wait_for_element(driver, by, value, timeout=5):
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
    except TimeoutException:
        print(f"Timeout waiting for element: {by}={value}")
        return None

def scrape_marker_data(driver, marker):
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            # Scroll the marker into view
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center', inline: 'center'});", marker)
            time.sleep(2)  # Increased delay after scrolling

            # Try to click using different methods
            try:
                ActionChains(driver).move_to_element(marker).click().perform()
            except:
                try:
                    driver.execute_script("arguments[0].click();", marker)
                except:
                    marker.click()

            # Wait for the info window to appear
            info_window = wait_for_element(driver, By.CLASS_NAME, 'gm-style-iw-c', timeout=5)  # Increased timeout
            
            if info_window:
                # Find the table within the info window
                table = info_window.find_element(By.CLASS_NAME, 'iw-table')
                screenshot_filename = f"success_screenshot_{time.time()}.png"
                screenshot_path = os.path.join('..', 'data', screenshot_filename)
                driver.save_screenshot(screenshot_path)
                print(f"Screenshot saved: {screenshot_path}")
                
                # Extract data from table rows
                rows = table.find_elements(By.TAG_NAME, 'tr')[1:]  # Skip header row
                data = []
                for row in rows:
                    cells = row.find_elements(By.TAG_NAME, 'td')
                    ip_address = cells[0].text if len(cells) > 0 else "N/A"
                    hostname = cells[1].text if len(cells) > 1 else "N/A"
                    volume = cells[2].text if len(cells) > 2 else "N/A"
                    email_type = cells[3].text if len(cells) > 3 else "N/A"
                    
                    print(f"IP Address: {ip_address}")
                    print(f"Hostname: {hostname}")
                    print(f"Last Day Volume: {volume}")
                    print(f"Email Type: {email_type}")
                    print("---")
                    
                    data.append([ip_address, hostname, volume, email_type])
                
                # Close the info window using JavaScript
                close_button = info_window.find_element(By.CLASS_NAME, 'gm-ui-hover-effect')
                driver.execute_script("arguments[0].click();", close_button)
                time.sleep(2)  # Wait after closing the info window
                return data  # Return the scraped data
            else:
                print("Info window did not appear")
        
        except (ElementClickInterceptedException, ElementNotInteractableException) as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(3)  # Increased wait before retrying
        except Exception as e:
            print(f"Unexpected error: {e}")
            driver.save_screenshot(f"error_screenshot_{time.time()}.png")
            return []  # Return empty list on unexpected errors

    print(f"Failed to scrape marker after {max_attempts} attempts")
    return []

def save_to_csv(data, base_filename):
    # Generate filename with current date and timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{base_filename}_{timestamp}.csv"
    
    # Create the full path for the file in the existing data folder
    filepath = os.path.join('..', 'data', filename)

    with open(filepath, 'w', newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        # Write the header row for the CSV file
        writer.writerow(["IP Address", "Host Name", "Last Day Volume", "Email Type"])
        writer.writerows(data)
    
    print(f"# Data saved to {filepath} #")
    
    return filepath

# Remove duplicate rows from the CSV file
def remove_duplicates(input_file, output_file):
    unique_rows = OrderedDict()

    with open(input_file, 'r', newline = "") as csvfile:
        reader = csv.reader(csvfile)
        headers = next(reader) # Read the header row

        for row in reader:
            # Skip empty rows
            if not any(row):
                continue
        
            # Use tuple of row values as a key to ensure uniqueness
            row_key = tuple(row)
            unique_rows[row_key] = row
    
    # Write the unique rows to the output file
    with open(output_file, 'w', newline = "") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers) # Write the header row
        writer.writerows(unique_rows.values()) # Write the unique crawl data as rows
    
    print(f"# Duplicate rows removed. Data saved to {output_file} #")

def get_all_malware_markers(driver):
    # Get individual markers
    individual_markers = driver.find_elements(By.CSS_SELECTOR, 
        '.map-container div[title="Malware"][aria-label="Malware"][role="button"]')
    
    # Get cluster markers
    cluster_markers = driver.find_elements(By.CSS_SELECTOR, 
        '.map-container div[class="malware-cluster"][title="Malware"][style*="cursor: pointer"]')
    
    print(f"Found {len(individual_markers)} individual markers and {len(cluster_markers)} cluster markers")
    
    # Combine both sets
    return individual_markers + cluster_markers


def main():
    driver = setup_driver()
    all_data = []
    try:
        print("Navigating to the page...")
        driver.get("https://www.talosintelligence.com/reputation_center/")
        
        # Wait for the map to load
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'map-container'))
        )
        print("Page loaded. Current URL:", driver.current_url)
        
        # Uncheck "Legitimate Email" and "Spam" buttons
        uncheck_buttons(driver)
        
        # Wait for the map to update
        time.sleep(5)
        
        # Find all malware markers
        malware_markers = get_all_malware_markers(driver)
        
        print(f"Found {len(malware_markers)} Malware markers:")
        
        # Shuffle the markers to randomize the order
        random.shuffle(malware_markers)
        
        for i, marker in enumerate(malware_markers, 1):
            print(f"Processing Marker {i}:")
            data = scrape_marker_data(driver, marker)
            all_data.extend(data)
            time.sleep(random.uniform(2, 5))  # Increased random delay between markers
        
    finally:
        driver.quit()
    
    # Save all scraped data to CSV with timestamp
    base_filename = 'result-malware-after-adjust-css-selector'
    csv_file = save_to_csv(all_data, base_filename)
    print(f"Scraped data saved to {csv_file}")

    # Remove duplicates
    unique_base_filename = 'result-malware-unique'
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_csv_file = f"{unique_base_filename}_{timestamp}.csv"
    remove_duplicates(csv_file, unique_csv_file)

# Function to uncheck the buttons
def uncheck_buttons(driver):
    buttons_to_uncheck = ['legit-button', 'spam-button']
    for button_id in buttons_to_uncheck:
        try:
            button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, button_id))
            )
            
            print(button)
            if button.get_attribute('value') in ['legit', 'spam']:
                driver.execute_script("arguments[0].click();", button)
            print(f"Unchecked {button_id}")
        except Exception as e:
            print(f"Error unchecking {button_id}: {e}")

if __name__ == "__main__":
    main()
