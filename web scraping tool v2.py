import signal
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time

# Initialize the WebDriver (ensure you have the appropriate driver installed and in your PATH)
driver = webdriver.Chrome()  # or webdriver.Firefox() for Firefox

# Open Google Maps with the search
driver.get("https://www.google.com/maps/search/chinese+restaurant/@34.0681915,-118.2306268,11.74z?entry=ttu")

# Wait for the page to load completely
time.sleep(5)

# Initialize an empty list to store the results
results = []

# Find the scrollable search panel element
search_panel = driver.find_element(By.CSS_SELECTOR, 'div[aria-label="Results for chinese restaurant"]')

# Function to scroll the search panel
def scroll_panel(panel):
    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", panel)
    time.sleep(3)

# Function to scroll to the element and click
def scroll_to_element_and_click(element):
    driver.execute_script("arguments[0].scrollIntoView(true);", element)
    time.sleep(3)  # Wait for the scrolling to complete
    element.click()

# Function to save data to CSV
def save_data(data):
    df = pd.DataFrame(data)
    df.to_csv('chinese_restaurant_la.csv', index=False)
    print("Data saved to chinese_restaurant_la.csv")

# Signal handler to catch keyboard interrupts and save data
def signal_handler(sig, frame):
    print('You pressed Ctrl+C! Saving data and exiting...')
    save_data(results)
    driver.quit()
    sys.exit(0)

# Register the signal handler
signal.signal(signal.SIGINT, signal_handler)

# Track already processed listing URLs to avoid re-processing
processed_urls = set()

# Loop through each listing and extract the necessary information
while True:
    # Refresh the listings each time because the page might re-render after each click
    listings = driver.find_elements(By.CLASS_NAME, 'Nv2PK')
    new_data_collected = False

    for i in range(len(listings)):
        try:
            # Refresh the listings within the loop to ensure it is up-to-date
            listings = driver.find_elements(By.CLASS_NAME, 'Nv2PK')
            if i >= len(listings):
                break
            listing = listings[i]

            # Get the URL of the listing to check if it has been processed
            listing_url = listing.find_element(By.TAG_NAME, 'a').get_attribute('href')

            # Skip the listing if it has already been processed
            if listing_url in processed_urls:
                continue

            # Scroll to the listing and click on it to expand the tab
            scroll_to_element_and_click(listing)

            # Wait for the tab to expand and load its contents
            time.sleep(5)
            print("Listing HTML:\n", listing.get_attribute('innerHTML'))

            try:
                name = driver.find_element(By.CLASS_NAME, 'DUwDvf').text  # Adjust the class name as per the actual HTML structure
            except:
                name = "N/A"

            try:
                address = driver.find_element(By.CLASS_NAME, 'Io6YTe').text  # Adjust the class name as per the actual HTML structure
            except:
                address = "N/A"
            # Locate the phone number using the href attribute containing 'tel:'
            phone_element = WebDriverWait(driver, 10).until(
              EC.presence_of_element_located((By.XPATH, ".//a[contains(@href, 'tel:')]"))
            )
            phone = phone_element.get_attribute('href').replace('tel:', '')
            # print(f"Found phone number: {phone}")

            try:
              website_element = driver.find_element(By.CSS_SELECTOR, 'a.CsEnBe')
              website_url = website_element.get_attribute('href')
              # print(f"Found website URL: {website_url}")
            except Exception as e:
              # print(f"Failed to find website URL: {e}")
              website_url = "N/A"

            try:
              # Debugging: Print the HTML content of the listing
              # print("Listing HTML:\n", listing.get_attribute('innerHTML'))
              # Locate the price element using the provided HTML structure
              price_element = listing.find_element(By.XPATH, './/span[@aria-label[contains(., "Price:")]]')
              price = price_element.text
              # print(f"Found price: {price}")
            except Exception as e:
              # print(f"Failed to find price: {e}")
              price = "N/A"

            try:
                reviews = driver.find_element(By.CLASS_NAME, 'F7nice').text  # Adjust the class name as per the actual HTML structure
            except:
                reviews = "N/A"

            # Append the extracted information to the list
            results.append({"Name": name, "Address": address, "Phone": phone,
                             "price": price, "Reviews": reviews, "website": website_url})

            # Add the listing URL to the set of processed URLs
            processed_urls.add(listing_url)

            # Set flag indicating new data was collected
            new_data_collected = True

            # Close the expanded tab by pressing the Escape key
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)

            # Wait for the tab to close
            time.sleep(2)
            print(f"Result count after iteration: {len(results)}")
        except Exception as e:
            print(f"Error processing listing {i}: {e}")

    # Break the loop if no new data was collected in this iteration
    if not new_data_collected:
        break

    # Scroll the search panel to load more results
    scroll_panel(search_panel)

# Quit the WebDriver and save data after the loop completes
driver.quit()
save_data(results)
