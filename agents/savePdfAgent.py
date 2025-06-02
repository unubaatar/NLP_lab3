from fpdf import FPDF
import os

class PDFReportAgent:
    def __init__(self, filename="report.pdf"):
        self.filename = filename
        self.pdf = FPDF()
        self.pdf.add_page()

        font_path = os.path.join("fonts", "DejaVuSans.ttf")
        self.pdf.add_font("DejaVu", "", font_path, uni=True)
        self.pdf.set_font("DejaVu", size=12)

    def _write_title(self, title):
        self.pdf.set_font("DejaVu", size=14)
        self.pdf.ln(5)
        self.pdf.set_text_color(0, 0, 128)
        self.pdf.cell(0, 10, txt=title, ln=True, align='L')
        self.pdf.set_text_color(0, 0, 0)
        self.pdf.set_font("DejaVu", size=12)
        self.pdf.ln(2)

    def _write_list_item(self, text):
        self.pdf.cell(10)  # indent
        self.pdf.multi_cell(0, 8, txt=f"• {text}")
        self.pdf.ln(1)

    def generate(self, df, tavily_results=None):
        self._write_title(" Үл хөдлөх хөрөнгийн дэлгэрэнгүй тайлан ")

        # 1. Өрөөний тоогоор ангилсан байрны тоо
        self._write_title("1. Өрөөний тоогоор ангилсан байрны тоо")
        room_counts = df['rooms'].value_counts(dropna=True).sort_index()
        for room, count in room_counts.items():
            self._write_list_item(f"{room} өрөөтэй нийт {count} байр байна.")

        # 2. Өрөө тус бүрийн дундаж үнэ
        self._write_title("2. Өрөө тус бүрийн дундаж үнэ (сая ₮)")
        avg_price_by_room = df.groupby('rooms')['price_mn'].mean().sort_index()
        for room, avg_price in avg_price_by_room.items():
            self._write_list_item(f"{room} өрөөтэй байрны дундаж үнэ {avg_price:.1f} сая төгрөг байна.")

        # 3. Цонхны тоогоор ангилсан байрны тоо
        self._write_title("3. Цонхны тоогоор ангилсан байрны тоо")
        window_counts = df['Number_of_Windows'].value_counts(dropna=True).sort_index()
        for win, count in window_counts.items():
            self._write_list_item(f"{win} цонхтой нийт {count} байр бүртгэгдсэн байна.")

        # 4. Цонхны тоонд тулгуурласан дундаж үнэ
        self._write_title("4. Цонхны тоонд тулгуурласан дундаж үнэ")
        avg_price_by_window = df.groupby('Number_of_Windows')['price_mn'].mean().sort_index()
        for win, avg_price in avg_price_by_window.items():
            self._write_list_item(f"{win} цонхтой байрны дундаж үнэ {avg_price:.1f} сая төгрөг байна.")

        # 5. Tavily AI хайлтын эхний 5 үр дүн
        self._write_title("5. Tavily AI хайлтын эхний 5 үр дүн")
        if tavily_results:
            for i, res in enumerate(tavily_results[:5], 1):
                title = res.get("title", "Гарчиг байхгүй")
                url = res.get("url", "Холбоос байхгүй")
                self._write_list_item(f"{i}. {title}\n   Холбоос: {url}")
        else:
            self._write_list_item("Tavily-аас үр дүн ирээгүй байна.")

        self.pdf.output(self.filename)
        print(f"\n📄 Тайлан PDF файл болгон хадгалагдлаа: {self.filename}")
