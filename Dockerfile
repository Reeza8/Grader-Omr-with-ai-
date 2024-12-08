FROM python:3.12-slim

# نصب Bash و کتابخانه‌های مورد نیاز

# نصب ابزارهای مورد نیاز برای کامپایل و کار با PostgreSQL
RUN apt-get update && \
    apt-get install -y \
    gcc \
    libpq-dev \
    libgl1-mesa-glx \
    libglib2.0-0 && \
    apt-get clean && rm -rf /var/lib/apt/lists/* \

# تنظیم دایرکتوری کاری
WORKDIR /app

# نصب وابستگی‌ها از requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# کپی کردن سایر فایل‌ها
COPY . .

# فرمان اجرای اپلیکیشن
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
