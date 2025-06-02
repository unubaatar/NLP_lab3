import pandas as pd
import re
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

from agents.paramBuildAgent import build_search_params
from agents.regexAgent import parse_user_input
from agents.savePdfAgent import PDFReportAgent
from agents.tavilySearchAgent import TavilySearchAgent
from agents.uneguiScapingAgent import UneguiAgent

def prepare_dataframe(data):
    df = pd.DataFrame(data)

    # Өрөөний тоо
    def extract_rooms(text):
        m = re.search(r'(\d+)\s*өрөө', str(text))
        return int(m.group(1)) if m else None
    df['rooms'] = df['Name'].apply(extract_rooms)

    # Цонхны тоо гаргах
    def extract_windows(text):
        m = re.search(r'(\d+)\s*цонх', str(text))
        return int(m.group(1)) if m else None
    df['window_count'] = df['Name'].apply(extract_windows)

    # Үнэ (сая ₮) numeric болгож ялгах
    def extract_price(price_str):
        price_str = str(price_str).replace(',', '')
        match = re.search(r'(\d+(?:\.\d+)?)', price_str)
        return float(match.group(1)) if match else None
    df['price_mn'] = df['Price'].apply(extract_price)

    return df

def generate_report(df, tavily_results=None):
    print("\n=== Үл хөдлөх хөрөнгийн тайлан ===")

    print("\n1. Өрөөний тоогоор ангилсан байрны тоо:")
    print(df['rooms'].value_counts(dropna=True))

    print("\n2. Өрөө тус бүрийн дундаж үнэ (сая ₮):")
    print(df.groupby('rooms')['price_mn'].mean())

    print("\n3. Цонхны тоогоор ангилсан байрны тоо:")
    print(df['Number_of_Windows'].value_counts(dropna=True))

    print("\n4. Цонхны тоонд тулгуурласан дундаж үнэ (сая ₮):")
    print(df.groupby('Number_of_Windows')['price_mn'].mean())

    print("\n5. Tavily AI хайлтын эхний 5 үр дүн:")
    if tavily_results:
        for i, res in enumerate(tavily_results[:5], 1):
            title = res.get('title', 'Гарчиг байхгүй')
            url = res.get('url', 'Холбоос байхгүй')
            print(f"{i}. {title}\n   Холбоос: {url}")
    else:
        print("Tavily-аас үр дүн ирээгүй байна.")

def main():
    user_text = input("Текстээ оруулна уу: ")

    # 1. Хэрэглэгчийн текстийг задлах
    parsed = parse_user_input(user_text)
    print("Олдсон өгөгдөл:", parsed)

    # 2. Хайлтын параметр үүсгэх
    search_params = build_search_params(parsed)
    print("Хайлтын параметрүүд:", search_params)

    # 3. Зар хайх
    agent = UneguiAgent(delay=1)
    listings = agent.scrape_listings(search_params, limit=5)

    if not listings:
        print("Зар олдсонгүй.")
        return

    # 4. DataFrame бэлтгэх
    df = prepare_dataframe(listings)

    # 5. Tavily AI хайлт
    tavily_agent = TavilySearchAgent(api_key="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")
    tavily_results = tavily_agent.search(user_text, num_results=5)

    # 6. Тайлан хэвлэх
    generate_report(df, tavily_results)
    
    pdf_agent = PDFReportAgent(filename="apartment_report.pdf")
    pdf_agent.generate(df, tavily_results)

if __name__ == "__main__":
    main()
