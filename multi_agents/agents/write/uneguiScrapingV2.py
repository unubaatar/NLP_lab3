import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote, urljoin
import json
import time

def get_adv_urls(main_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(main_url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching main page: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all('a')
    
    base_url = 'https://www.unegui.mn'
    adv_urls = [urljoin(base_url, link.get('href')) for link in links if link.get('href') and 'adv' in link.get('href')]
    return list(set(adv_urls))  # Remove duplicates

def scrape_listing_data(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching listing page {url}: {e}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract name (title)
    title_elem = soup.find('h1', class_='title-announcement')
    name = title_elem.get_text(strip=True) if title_elem else 'N/A'
    
    # Extract price
    price_elem = soup.find('div', class_='announcement-price__cost')
    price = price_elem.get_text(strip=True) if price_elem else 'N/A'

    # Initialize data dictionary with basic fields
    data = {
        'Name': name,
        'Price': price,
        'URL': url
    }

    # Extract all characteristics from the chars-column section
    chars_list = soup.find('ul', class_='chars-column')
    if chars_list:
        for item in chars_list.find_all('li'):
            key_elem = item.find('span', class_='key-chars')
            value_elem = item.find('span', class_='value-chars')
            
            if key_elem and value_elem:
                key = key_elem.get_text(strip=True).replace(':', '').strip()  # Remove colon and extra spaces
                value = value_elem.get_text(strip=True)
                # Map to English keys for consistency
                key_mapping = {
                    'өрөө': 'Rooms',
                    'шинэ': 'Type',
                    'талбай': 'Area',
                    'тагт': 'Balcony',
                    'ашиглалтын осон он': 'Year_of_Use',
                    'худалдааны объект': 'Commercial_Object',
                    'телевизийн холболт (horizontal)': 'TV_Connection',
                    'гараж': 'Garage',
                    'лооных': 'Loggia',
                    'барилгын давхар': 'Building_Floors',
                    'хаалга': 'Door',
                    'ямар давхар': 'Floor_Number',
                    'цахилгаан шат': 'Elevator',
                    'барилгын нийт давхар': 'Total_Building_Floors',
                    'цонхны тоо': 'Number_of_Windows',
                    'лоджи': 'Loggia',  # Alternative spelling
                    'тоо': 'Rooms'  # Alternative for number of rooms
                }
                # Use mapped key if available, otherwise use the raw key
                mapped_key = key_mapping.get(key.lower(), key)
                data[mapped_key] = value

    return data

def main():
    main_url = 'https://www.unegui.mn/l-hdlh/l-hdlh-zarna/'
    decoded_url = unquote(main_url)
    print(f"Scraping 'adv' URLs from: {decoded_url}\n")

    adv_urls = get_adv_urls(main_url)
    
    if not adv_urls:
        print("No 'adv' URLs found.")
        return

    # Limit to first 5 adv URLs
    adv_urls = adv_urls[:5]
    print(f"Found {len(adv_urls)} 'adv' URLs (limited to first 5). Scraping data...\n")
    
    listings_data = []
    for idx, url in enumerate(adv_urls, 1):
        print(f"Scraping listing {idx}/{len(adv_urls)}: {url}")
        data = scrape_listing_data(url)
        if data:
            listings_data.append(data)
        time.sleep(1)  # Delay to avoid overwhelming the server

    if listings_data:
        # Save to JSON
        with open('unegui_all_adv_listings.json', 'w', encoding='utf-8') as f:
            json.dump(listings_data, f, ensure_ascii=False, indent=4)
        
        print("\nData saved to unegui_all_adv_listings.json")
        print("\nScraped data:")
        for listing in listings_data:
            print("\nListing:")
            for key, value in listing.items():
                print(f"{key}: {value}")
        print(f"\nTotal listings scraped: {len(listings_data)}")
    else:
        print("No data scraped.")

if __name__ == "__main__":
    main()