import json
import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import re

from agents.paramBuildAgent import build_search_params
from agents.regexAgent import parse_user_input
from agents.uneguiScapingAgent import UneguiAgent
from agents.savePdfAgent import ReportAgent

def prepare_dataframe(data):
    df = pd.DataFrame(data)
    
    # Text field-үүдийг нэгтгэх
    def combine_text(row):
        parts = [str(row.get(k, '')) for k in ['Name', 'Price', 'Balcony', 'Garage', 'Цонх', 'Шал', 'Door']]
        return ' | '.join(parts)
    df['combined_text'] = df.apply(combine_text, axis=1)

    # Дүүрэг олох
    district_list = ["Хан уул", "Сонгино хайрхан", "Баянгол", "Чингэлтэй", "Багануур"]
    df['district'] = df['Name'].apply(lambda x: next((d for d in district_list if d in x), 'Бусад'))

    # Өрөөний тоо олох
    def extract_rooms(text):
        m = re.search(r'(\d+)\s*өрөө', str(text))
        return int(m.group(1)) if m else None
    df['rooms'] = df['Name'].apply(extract_rooms)

    # Үнэ олох (сая төгрөгөөр)
    def extract_price(price_str):
        m = re.search(r'(\d+)', str(price_str).replace(',', ''))
        return int(m.group(1)) if m else None
    df['price_mn'] = df['Price'].apply(extract_price)
    
    return df

def build_faiss_index(embeddings):
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    return index

def generate_report(df):
    print("\n=== Үл хөдлөх хөрөнгийн тайлан ===")
    print("\n1. Дүүрэг тус бүрт байрны тоо:")
    print(df['district'].value_counts())
    print("\n2. Өрөөний тоогоор ангилсан байрны тоо:")
    print(df['rooms'].value_counts(dropna=True))
    print("\n3. Үнийн статистик (сая төгрөгөөр):")
    print(df['price_mn'].describe())
    print("\n4. Жишээ байрны мэдээлэл:")
    print(df[['Name', 'Price', 'rooms', 'district']].head())

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

        # DataFrame бэлтгэх
        df = prepare_dataframe(listings)

        # Embedding үүсгэх
        model = SentenceTransformer('all-MiniLM-L6-v2')
        embeddings = model.encode(df['combined_text'].tolist())

        # FAISS индекс үүсгэх
        index = build_faiss_index(np.array(embeddings))

        # Тайлан гаргах
        generate_report(df)
        # PDF файл үүсгэх
        # report_agent = ReportAgent("unegui_real_estate_report.pdf")
        # report_agent.generate(df)

    else:
        print("Зар олдсонгүй.")

if __name__ == "__main__":
    main()