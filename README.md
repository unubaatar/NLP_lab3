# Энэ коммандаар virtual env тааруулаарай broders 
python -m venv venv

# Тэгээд энүүгээр activate хийгээд  
venv\Scripts\activate

# Аан харин энүүгээр болхоороо сангуудаа install хийхийн байнлээ 
pip install -r requirements.txt 

# Энүүгээр тэгээд web ээ ажиллуулна гэсэн. ( localhost: 8k дээр )
adk web 

