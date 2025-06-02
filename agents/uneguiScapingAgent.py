import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote
import json
import time

class UneguiAgent:
    def __init__(self, base_url='https://www.unegui.mn/l-hdlh/l-hdlh-zarna/', delay=1):
        self.base_url = base_url
        self.delay = delay
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def build_query_string(self, params):
        parts = []
        for key, value in params.items():
            if key == 'q' and isinstance(value, list):
                query_value = ' '.join(value)
                encoded_value = quote(query_value)
            else:
                encoded_value = quote(str(value))
            parts.append(f"{key}={encoded_value}")
        return '&'.join(parts)

    def get_adv_urls(self, query_string):
        url = f"{self.base_url}?{query_string}" if query_string else self.base_url
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching main page {url}: {e}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a')

        adv_urls = [
            urljoin('https://www.unegui.mn', link.get('href'))
            for link in links if link.get('href') and 'adv' in link.get('href')
        ]

        return list(set(adv_urls))

    def scrape_listing_data(self, url):
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching listing page {url}: {e}")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')

        title_elem = soup.find('h1', class_='title-announcement')
        name = title_elem.get_text(strip=True) if title_elem else 'N/A'

        price_elem = soup.find('div', class_='announcement-price__cost')
        price = price_elem.get_text(strip=True) if price_elem else 'N/A'

        data = {'Name': name, 'Price': price, 'URL': url}

        chars_list = soup.find('ul', class_='chars-column')
        if chars_list:
            for item in chars_list.find_all('li'):
                key_elem = item.find('span', class_='key-chars')
                value_elem = item.find('span', class_='value-chars')
                if key_elem and value_elem:
                    key = key_elem.get_text(strip=True).replace(':', '').strip()
                    value = value_elem.get_text(strip=True)
                    # Хэлний болон нэрийн хөрвүүлэлт
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
                        'лоджи': 'Loggia',
                        'тоо': 'Rooms'
                    }
                    mapped_key = key_mapping.get(key.lower(), key)
                    data[mapped_key] = value

        return data

    def scrape_listings(self, params, limit=5):
        query_string = self.build_query_string(params)
        adv_urls = self.get_adv_urls(query_string)
        if not adv_urls:
            print("No advertisement URLs found.")
            return []

        adv_urls = adv_urls[:limit]
        results = []
        for idx, url in enumerate(adv_urls, 1):
            print(f"Scraping listing {idx}/{len(adv_urls)}: {url}")
            data = self.scrape_listing_data(url)
            if data:
                results.append(data)
            time.sleep(self.delay)

        return results

    def save_to_json(self, data, filename='listings.json'):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Data saved to {filename}")

