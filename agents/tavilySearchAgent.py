import requests

class TavilySearchAgent:
    def __init__(self, api_key):
        self.api_key = api_key
        self.url = "https://api.tavily.com/search"
        self.headers = {"Content-Type": "application/json"}

    def search(self, query, num_results=5):
        payload = {
            "api_key": self.api_key,
            "query": query,
            "search_depth": "basic",
            "max_results": num_results
        }
        try:
            response = requests.post(self.url, json=payload, headers=self.headers, timeout=10)
            response.raise_for_status()
            results = response.json().get("results", [])
            return [{"title": r["title"], "url": r["url"]} for r in results]
        except requests.RequestException as e:
            print(f"[Network Error]: {e}")
            return []
        except Exception as e:
            print(f"[Parse Error]: {e}")
            return []
