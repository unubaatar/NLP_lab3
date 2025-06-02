from fpdf import FPDF
import pandas as pd


class ReportAgent:
    def __init__(self, filename="real_estate_report.pdf"):
        self.filename = filename
        self.pdf = FPDF()
        self.pdf.set_auto_page_break(auto=True, margin=15)
        # Фонт оруулах
        self.pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)

    def generate(self, df: pd.DataFrame):
        self.pdf.add_page()
        self.pdf.set_font("DejaVu", size=12)

        self._add_title("Үл хөдлөх хөрөнгийн тайлан")
        self._add_district_section(df)
        self._add_room_section(df)
        self._add_price_statistics(df)
        self._add_sample_listings(df)

        self._save()

    def _add_title(self, title):
        self.pdf.set_font("DejaVu", style='', size=14)
        self.pdf.cell(0, 10, title, ln=True, align='C')
        self.pdf.set_font("DejaVu", size=12)
        self.pdf.ln(10)

    def _add_district_section(self, df):
        self.pdf.cell(0, 10, "1. Дүүрэг тус бүрт байрны тоо:", ln=True)
        district_counts = df['district'].value_counts()
        for district, count in district_counts.items():
            self.pdf.cell(0, 10, f"{district}: {count}", ln=True)
        self.pdf.ln(5)

    def _add_room_section(self, df):
        self.pdf.cell(0, 10, "2. Өрөөний тоогоор ангилсан байрны тоо:", ln=True)
        rooms_counts = df['rooms'].value_counts(dropna=True)
        for rooms, count in rooms_counts.items():
            self.pdf.cell(0, 10, f"{rooms} өрөө: {count}", ln=True)
        self.pdf.ln(5)

    def _add_price_statistics(self, df):
        self.pdf.cell(0, 10, "3. Үнийн статистик (сая төгрөгөөр):", ln=True)
        desc = df['price_mn'].describe()
        for stat_name, stat_value in desc.items():
            self.pdf.cell(0, 10, f"{stat_name}: {stat_value:.2f}", ln=True)
        self.pdf.ln(5)

    def _add_sample_listings(self, df):
        self.pdf.cell(0, 10, "4. Жишээ байрны мэдээлэл:", ln=True)
        sample = df[['Name', 'Price', 'rooms', 'district']].head()
        for idx, row in sample.iterrows():
            line = f"{idx+1}. {row['Name']} | Үнэ: {row['Price']} | Өрөө: {row['rooms']} | Дүүрэг: {row['district']}"
            self.pdf.multi_cell(0, 10, line)
        self.pdf.ln(5)

    def _save(self):
        self.pdf.output(self.filename)
        print(f"\n✅ Тайлан {self.filename} нэртэй PDF файлд хадгалагдлаа.")
