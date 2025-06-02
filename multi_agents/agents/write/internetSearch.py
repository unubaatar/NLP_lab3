import requests

def search_tavily(query, num_results=5, api_key="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"):
    url = "https://api.tavily.com/search"

    headers = {
        "Content-Type": "application/json"
    }

    payload = {
        "api_key": api_key,
        "query": query,
        "search_depth": "basic",
        "max_results": num_results
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json()
        results = data.get("results", [])
        
        return [{"title": r["title"], "url": r["url"]} for r in results]

    except requests.RequestException as e:
        print(f"[Network Error]: {e}")
        return []
    except Exception as e:
        print(f"[Parse Error]: {e}")
        return []

# Example usage
if __name__ == "__main__":
    API_KEY = "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"  # Та энд өөрийн API key-ээ оруулна
    query = "Хан-Уул дүүрэг байр"
    
    results = search_tavily(query, num_results=5, api_key=API_KEY)

    if results:
        print(f"\nTop {len(results)} Tavily search results for '{query}':\n")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['title']}")
            print(f"   URL: {result['url']}\n")
    else:
        print("No results found or an error occurred.")
