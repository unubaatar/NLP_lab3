import requests
from bs4 import BeautifulSoup
import urllib.parse
import time

def search_bing(query, num_results=5):
    # Encode the query for URL
    encoded_query = urllib.parse.quote(query)
    url = f"https://www.bing.com/search?q={encoded_query}"
    print(f"Searching URL: {url}")
    
    # Set headers to mimic a browser
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive"
    }
    
    try:
        # Send HTTP request
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        print(f"Response status code: {response.status_code}")
        
        # Parse HTML content
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Debugging: Save HTML for inspection (optional)
        # with open("bing_response.html", "w", encoding="utf-8") as f:
        #     f.write(soup.prettify())
        
        # Find search result elements
        results = soup.find_all("li", class_="b_algo")
        if not results:
            print("No 'b_algo' class found, trying alternative selector...")
            results = soup.select("div.b_algo, li[data-bm], div.b_result")[:num_results * 2]  # Overshoot to filter later
        
        # Extract title and URL, ensuring uniqueness and validity
        search_results = []
        seen_urls = set()
        seen_titles = set()
        
        for result in results:
            if len(search_results) >= num_results:
                break
                
            title_elem = result.find("h2") or result.find("h3") or result.find(class_="b_title")
            link_elem = result.find("a", href=True)
            
            if title_elem and link_elem:
                title = title_elem.get_text(strip=True)
                url = link_elem["href"]
                
                # Validate URL
                if not url.startswith(("http://", "https://")):
                    print(f"Skipping invalid URL: {url}")
                    continue
                
                # Check for duplicates
                if url in seen_urls or title in seen_titles:
                    print(f"Skipping duplicate: {title}")
                    continue
                
                # Add to results
                search_results.append({"title": title, "url": url})
                seen_urls.add(url)
                seen_titles.add(title)
            else:
                print(f"Skipping result due to missing title or URL: {result.get_text(strip=True)[:50]}...")
        
        if not search_results:
            print("No valid results found. Check HTML structure or try again.")
        
        return search_results
    
    except requests.RequestException as e:
        print(f"Network error fetching search results: {e}")
        return []
    except Exception as e:
        print(f"Error parsing search results: {e}")
        return []

# Example usage
if __name__ == "__main__":
    query = "Хан уул дүүрэг байр"
    results = search_bing(query, num_results=5)
    
    # Display results
    if results:
        print(f"\nTop {len(results)} Bing search results for '{query}':\n")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['title']}")
            print(f"   URL: {result['url']}\n")
    else:
        print("No results found or an error occurred.")
    
    # Add delay to avoid rate-limiting
    time.sleep(1)
