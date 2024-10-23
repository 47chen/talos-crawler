# Talos Intelligence Malware Scraper

## Introduction
This project is a web scraper designed to extract malware-related data from the Talos Intelligence Reputation Center. It automates the process of gathering information about malware markers on their interactive map, providing valuable insights for cybersecurity research and analysis.

## Project Overview and Features

- **Automated Web Scraping**: Utilizes Selenium WebDriver to navigate and interact with the Talos Intelligence website.
- **Stealth Operation**: Implements random user agents and headless browsing to mimic human-like behavior and avoid detection.
- **Data Extraction**: Scrapes detailed information from malware markers, including IP addresses, hostnames, volumes, and email types.
- **Error Handling**: Robust error handling and retry mechanisms to ensure reliable data collection.
- **Data Processing**: Removes duplicate entries and saves data in a structured CSV format.
- **Logging and Debugging**: Includes screenshot capture for successful scrapes and errors for easy debugging.

## Packages Used

- **selenium**: Core package for browser automation and web scraping.
- **webdriver_manager**: Automatic management of WebDriver binaries.
- **time & random**: For implementing delays and randomization to mimic human behavior.
- **csv**: For saving scraped data in CSV format.
- **datetime**: To generate timestamps for file naming.
- **collections**: Used for removing duplicate entries efficiently.

## Setup and Usage

Follow these steps to set up and run the scraper:

1. **Clone the Repository**
   ```
   git clone https://github.com/47chen/talos-crawler.git
   cd talos-crawle
   ```

2. **Set Up a Virtual Environment** (Optional but recommended)
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Required Packages**
   ```
   pip install selenium webdriver-manager
   ```

4. **Install Firefox Browser**
   Ensure that Firefox is installed on your system as this script uses the Firefox WebDriver.

5. **Run the Scraper**
   ```
   python src/my_scraper.py
   ```

6. **Check the Results**
   After the script finishes running, check the `data` folder for the output CSV files.

## Notes
- The scraper is configured to run in headless mode. If you want to see the browser in action, remove the `--headless` option in the `setup_driver` function.
- Adjust the sleep times and randomization as needed to suit the website's responsiveness and to avoid potential rate limiting.
- Always respect the website's terms of service and robots.txt file when scraping.

## Disclaimer
This tool is for educational and research purposes only. Ensure you have permission to scrape the target website and comply with all applicable laws and regulations.
