FROM python:3.12-slim

# نصب کتابخانه‌های مورد نیاز
RUN apt-get update && \
    apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0

# تنظیمات دیگر...
WORKDIR /app

# نصب وابستگی‌ها از requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# کپی کردن سایر فایل‌ها
COPY . .

# فرمان اجرای اپلیکیشن
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
