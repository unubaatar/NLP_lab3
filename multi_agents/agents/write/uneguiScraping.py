import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlencode
import time
import json
import re

# Headers to mimic a browser
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

# Function to fetch and parse a webpage
def fetch_page(url):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

# Function to clean text
def clean_text(text):
    if isinstance(text, str):
        return ' '.join(text.split()) if text.strip() else "Not found"
    elif hasattr(text, 'text'):
        return ' '.join(text.text.split()) if text.text.strip() else "Not found"
    return "Not found"

# Function to extract number from text
def extract_number(text, pattern=r'\d+'):
    match = re.search(pattern, text)
    return match.group() if match else "Not found"

# Function to classify text based on patterns
def classify_text(text, field_type):
    text = text.lower() if isinstance(text, str) else ""
    
    if field_type == "ad_type":
        if "өрөө" in text:
            return "Орон сууц"
        elif "газар" in text:
            return "Газар"
        elif "хаус" in text or "байшин" in text:
            return "Хаус"
        return "Not found"
    
    elif field_type == "construction_status":
        if "ашиглалтад орсон" in text:
            return "Ашиглалтад орсон"
        elif "баригдаж байна" in text:
            return "Баригдаж байна"
        return "Not found"
    
    elif field_type == "payment_terms":
        if "бэлэн төлөлт" in text:
            return "Бэлэн төлөлтөөр"
        elif "банкны зээл" in text or "зээлээр" in text:
            return "Банкны зээлээр"
        elif "тохиролцоно" in text:
            return "Тохиролцоно"
        return "Not found"
    
    return "Not found"

# Function to get search parameters from JSON input
def get_search_params(json_input):
    try:
        params = json.loads(json_input)
        # Exclude parameters with empty string values
        return {k: str(v) for k, v in params.items() if v and str(v).strip()}
    except json.JSONDecodeError as e:
        print(f"Invalid JSON input: {e}")
        return {}

# Construct search URL
def construct_search_url(params):
    base_url = "https://www.unegui.mn/new-buildings/"
    query_string = urlencode(params)
    return f"{base_url}?{query_string}" if query_string else base_url

# Example JSON input with search query (replace with actual input)
json_input = '''
{
    "q": "",
    "price_min": "100000",
    "price_max": "200000000",
    "square_meter_price_min": "200000",
    "square_meter_price_max": "8000000",
    "bedrooms": "3,4,5,gte_6",
    "bathrooms": "3,4,5,6",
    "building_class": "",
    "living_area_min": "",
    "living_area_max": "",
    "floor_min": "",
    "floor_max": ""
}
'''

# Step 1: Get search parameters from JSON
search_params = get_search_params(json_input)
if not search_params:
    print("No valid search parameters provided.")
    exit()

print(f"Search parameters: {search_params}")
search_url = construct_search_url(search_params)
print(f"Constructed search URL: {search_url}")

# Step 2: Fetch the search page and extract /newbuilding/ URLs
soup = fetch_page(search_url)
if not soup:
    print("Failed to fetch search page.")
    exit()

base_url = "https://www.unegui.mn"
newbuilding_urls = []
for a_tag in soup.find_all('a', href=True):
    href = a_tag['href']
    full_url = urljoin(base_url, href)
    if '/new-buildings/' in full_url:
        newbuilding_urls.append(full_url)

# Remove duplicates
newbuilding_urls = list(dict.fromkeys(newbuilding_urls))

# Step 3: Scrape details from each /newbuilding/ URL and store in a list
all_data = []
for newbuilding_url in newbuilding_urls[:5]:  # Limit to 5 URLs for brevity; remove limit for all URLs
    print("scraping data")
    soup = fetch_page(newbuilding_url)
    if not soup:
        print("data scrapped")
        continue

    # Extract key information
    details = {'URL': newbuilding_url}

    # Price
    price_tag = soup.find(['span', 'div'], class_=re.compile(r'\b.*Header_price.*\b', re.IGNORECASE))
    if price_tag:
        details['Price'] = clean_text(price_tag.text)
    else:
        content = soup.find('div', class_='content') or soup.find('div', class_='announcement-content') or soup.find('div', class_='building-details')
        price_text = content.text if content    else soup.text
        price_match = re.search(r'(\d+\s*(?:сая|миллион|мянган|tögrog|₮)(?:\s*–\s*\d+\s*(?:сая|миллион|мянган|tögrog|₮))?)', price_text, re.IGNORECASE)
        details['Price'] = price_match.group() if price_match else "Not found"

    # Area (Талбай)
    area_tag = soup.find(string=lambda x: x and ('м²' in x or 'Талбай' in x))
    if area_tag:
        area_text = area_tag.find_parent('div') or area_tag.find_parent('td') or area_tag
        area_match = re.search(r'(\d+\.?\d*\s*м²)', area_text.text)
        details['Area'] = area_match.group() if area_match else clean_text(area_text)
    else:
        details['Area'] = "Not found"

    # Title (Зарын нэр)
    title_tag = soup.find('h1') or soup.find('div', class_='title') or soup.find('div', class_='building-title')
    details['Title'] = clean_text(title_tag) if title_tag else "Not found"

    # Location (Байрлал)
    location_cleaned = "Not found"
    # Step 1: Try extracting from JSON-LD or structured data in <script> tags
    for script_tag in soup.find_all('script', type='application/ld+json'):
        try:
            json_data = json.loads(script_tag.string)
            if isinstance(json_data, dict) and 'location' in json_data:
                location_cleaned = clean_text(json_data['location'])
                break
            elif isinstance(json_data, dict) and 'address' in json_data:
                location_cleaned = clean_text(json_data['address'])
                break
        except (json.JSONDecodeError, TypeError):
            continue

    # Step 2: If not found in JSON-LD, try specific HTML elements
    if location_cleaned == "Not found":
        for tag in soup.find_all(['div', 'span', 'p'], class_=re.compile('location|address|building-details', re.I)):
            if tag.find_parent('script') is None and ('Байршил' in tag.text or 'Хан-Уул' in tag.text):
                location_cleaned = clean_text(tag.text)
                break
        else:
            # Step 3: Fallback to elements containing "Байршил"
            location_tag = soup.find(string=re.compile(r'Байршил\s*:', re.I))
            if location_tag and location_tag.find_parent('script') is None:
                location_text = location_tag.find_parent('div') or location_tag.find_parent('span') or location_tag.find_parent('p') or location_tag
                location_cleaned = clean_text(location_text)

    # Clean and validate location
    location_cleaned = re.sub(r'№\d+.*|Unegui\.mn.*', '', location_cleaned)
    details['Location'] = "Not found" if len(location_cleaned) > 500 else location_cleaned

    # Rooms (Өрөө)
    rooms_tag = soup.find(string=lambda x: x and ('Өрөөний тоо' in x or 'өрөө' in x))
    if rooms_tag:
        rooms_text = rooms_tag.find_parent('div') or rooms_tag.find_parent('td') or rooms_tag
        rooms_match = re.search(r'(\d+\s*өрөө)', rooms_text.text, re.IGNORECASE)
        details['Rooms'] = rooms_match.group() if rooms_match else clean_text(rooms_text)
    else:
        rooms_match = re.search(r'(\d+\s*өрөө)', details['Title'], re.IGNORECASE)
        details['Rooms'] = rooms_match.group() if rooms_match else "Not found"

    # Posted Date (Нийтэлсэн огноо)
    date_tag = soup.find('span', class_=re.compile('date|time|published|post-date', re.I)) or \
               soup.find('div', class_=re.compile('date|time|published|post-date', re.I)) or \
               soup.find(string=lambda x: x and ('Нийтэлсэн' in x or 'Огноо' in x))
    if date_tag:
        date_text = date_tag.text if isinstance(date_tag, str) else date_tag.text
        date_match = re.search(r'(\d{4}-\d{2}-\d{2}\s*\d{2}:\d{2}|Өнөөдөр\s*\d{2}:\d{2}|Өчигдөр\s*\d{2}:\d{2})', date_text, re.I)
        if date_match:
            date_value = date_match.group()
            if "Өнөөдөр" in date_value:
                date_value = re.sub(r'Өнөөдөр', '2025-06-01', date_value, flags=re.I)
            elif "Өчигдөр" in date_value:
                date_value = re.sub(r'Өчигдөр', '2025-05-31', date_value, flags=re.I)
            details['Posted Date'] = date_value
        else:
            details['Posted Date'] = "Not found"
    else:
        # Fallback: Check meta tags for publication date
        meta_date = soup.find('meta', property='article:published_time') or soup.find('meta', name='date')
        if meta_date and meta_date.get('content'):
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', meta_date['content'])
            details['Posted Date'] = date_match.group() if date_match else "Not found"
        else:
            details['Posted Date'] = "Not found"

    # Ad Number (Зарын дугаар)
    ad_num_tag = soup.find(string=lambda x: x and ('Зарын дугаар' in x or 'ID' in x))
    if ad_num_tag:
        ad_num_text = ad_num_tag.find_parent('div') or ad_num_tag.find_parent('span') or ad_num_tag
        ad_num_match = re.search(r'\d+', ad_num_text.text)
        details['Ad Number'] = ad_num_match.group() if ad_num_match else "Not found"
    else:
        details['Ad Number'] = extract_number(newbuilding_url.split('/new-buildings/')[1])

    # Ad Type (Зарын төрөл)
    # details['Ad Type'] = classify_text(details['Title'] + " " + (content.text if content else ""), "ad_type")

    # Extract additional fields from the announcement block
    announcement_block = soup.find('div', class_='announcement-content') or soup.find('div', class_='content') or soup.find('div', class_='building-details')
    announcement_text = announcement_block.text if announcement_block else ""

    # Balcony (Тагт)
    balcony_match = re.search(r'Тагт:\s*(1 тагттай|Тагтгүй)', announcement_text)
    details['Balcony'] = balcony_match.group(1) if balcony_match else "Not found"

    # Window (Цонх)
    window_match = re.search(r'Цонх:\s*(Вакум|Хуванцар|Модон)', announcement_text)
    details['Window'] = window_match.group(1) if window_match else "Not found"

    # Year of Completion (Ашиглалтанд орсон он)
    year_match = re.search(r'Ашиглалтанд орсон он:\s*(\d{4})', announcement_text)
    details['Year of Completion'] = year_match.group(1) if year_match else "Not found"

    # Garage (Гараж)
    garage_match = re.search(r'Гараж:\s*(Байгаа|Байхгүй)', announcement_text)
    details['Garage'] = garage_match.group(1) if garage_match else "Not found"

    # Building Floors (Барилгын давхар)
    building_floors_match = re.search(r'Барилгын давхар:\s*(\d+)', announcement_text)
    details['Building Floors'] = building_floors_match.group(1) if building_floors_match else "Not found"

    # Door (Хаалга)
    door_match = re.search(r'Хаалга:\s*(Төмөр|Бүргэд|Модон)', announcement_text)
    details['Door'] = door_match.group(1) if door_match else "Not found"

    # Floor Number (Хэдэн давхарт)
    floor_number_match = re.search(r'Хэдэн давхарт:\s*(\d+)', announcement_text)
    details['Floor Number'] = floor_number_match.group(1) if floor_number_match else "Not found"

    # Number of Windows (Цонхны тоо)
    windows_count_match = re.search(r'Цонхны тоо:\s*(\d+)', announcement_text)
    details['Number of Windows'] = windows_count_match.group(1) if windows_count_match else "Not found"

    # Elevator (Цахилгаан шаттай эсэх)
    elevator_match = re.search(r'Цахилгаан шаттай эсэх:\s*(Цахилгаан шаттай|Цахилгаан шатгүй)', announcement_text)
    details['Elevator'] = elevator_match.group(1) if elevator_match else "Not found"

    # Construction Status (Барилгын явц)
    const_status_tag = soup.find(string=lambda x: x and ('Барилгын явц' in x or 'Ашиглалтад орсон' in x))
    if const_status_tag:
        const_status_text = const_status_tag.find_parent('div') or const_status_tag.find_parent('td') or const_status_tag
        details['Construction Status'] = classify_text(const_status_text.text, "construction_status")
    else:
        details['Construction Status'] = "Not found"

    # Payment Terms (Төлбөрийн нөхцөл)
    payment_tag = soup.find(string=lambda x: x and ('Төлбөрийн нөхцөл' in x or 'Бэлэн төлөлт' in x or 'Зээлээр' in x))
    if payment_tag:
        payment_text = payment_tag.find_parent('div') or payment_tag.find_parent('td') or payment_tag
        details['Payment Terms'] = classify_text(payment_text.text, "payment_terms")
    else:
        details['Payment Terms'] = "Not found"

    # Description (Тайлбар)
    desc_tag = soup.find('div', class_='content') or soup.find('div', class_='announcement-content') or soup.find('div', class_='building-description')
    if desc_tag:
        desc_text = desc_tag.text.strip()
        desc_text = re.sub(r'(\d+\s*(?:сая|миллион|мянган|tögrog|₮))', '', desc_text)
        desc_text = re.sub(r'(Талбай:\s*\d+\.?\d*\s*м²|Байршил:.*?)(?=\n|$)', '', desc_text)
        desc_text = re.sub(r'(Шал|Тагт|Гараж|Цонх|Хаалга|Барилгын давхар|Хэдэн давхарт|Цонхны тоо|Цахилгаан шат|Ашиглалтанд орсон он|Барилгын явц|Төлбөрийн нөхцөл):.*?(?=\n|$)', '', desc_text)
        details['Description'] = clean_text(desc_text)
    else:
        details['Description'] = "Not found"

    all_data.append(details)
    print("data scrapped")
    time.sleep(1)  # Polite delay

# Step 4: Save data to JSON file
with open('unegui_listings.json', 'w', encoding='utf-8') as f:
    json.dump(all_data, f, ensure_ascii=False, indent=4)

print(f"\nTotal /newbuilding/ URLs found: {len(newbuilding_urls)}")
print("Data saved to unegui_listings.json")