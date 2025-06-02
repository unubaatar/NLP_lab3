from agents.paramBuildAgent import build_search_params
from agents.regexAgent import parse_user_input
from agents.uneguiScapingAgent import UneguiAgent


def main():
    # Текстийг хэрэглэгчээс авах
    user_text = input("Текстээ оруулна уу: ")

    # Текстээс өгөгдлийг задлах
    parsed = parse_user_input(user_text)
    print("Олдсон өгөгдөл:", parsed)

    # Хайлтын параметрүүд үүсгэх
    search_params = build_search_params(parsed)
    print("Хайлтын параметрүүд:", search_params)

    # UneguiAgent-ийг ашиглан хайлт хийх
    agent = UneguiAgent(delay=1)
    listings = agent.scrape_listings(search_params, limit=5)

    if listings:
        agent.save_to_json(listings, 'unegui_listings.json')
        print("\nХайлтын үр дүн:")
        for listing in listings:
            print(listing)
    else:
        print("Зар олдсонгүй.")

if __name__ == "__main__":
    main()
