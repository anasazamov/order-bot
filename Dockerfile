# 1. Pythonning rasmiy imajini olish
FROM python:3.12-slim

# 2. Ishchi katalogni yaratish
WORKDIR /app

# 3. Talab qilingan Python kutubxonalarini o'rnatish uchun requirements.txt faylini nusxalash
COPY requirements.txt .

# 4. Python kutubxonalarini o'rnatish
RUN pip install --no-cache-dir -r requirements.txt

# 5. Butun loyihani konteynerga nusxalash
COPY . .

# 6. So'nggi kutubxonalar va fayllarni o'rnatish
RUN pip install --no-cache-dir -r requirements.txt

# 7. Python botni ishga tushirish
CMD ["python", "main.py"]
