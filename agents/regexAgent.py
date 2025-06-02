import re

def parse_user_input(text):
    # Дүүрэг хайх
    district_list = ["Хан уул", "Сонгино хайрхан", "Баянгол", "Чингэлтэй", "Багануур"]
    pattern = '|'.join([re.escape(d) for d in district_list])
    districts = re.findall(pattern, text)

    # Өрөөний тоо олох
    rooms_match = re.search(r'(\d+)\s*өрөө', text)
    rooms = int(rooms_match.group(1)) if rooms_match else None

    # Үнэ олох (сая төгрөгөөр)
    price_match = re.search(r'(\d+)\s*сая', text)
    price = int(price_match.group(1)) if price_match else None

    return {
        "districts": districts,
        "rooms": rooms,
        "price": price
    }
