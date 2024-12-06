# انتخاب تصویر پایه
FROM python:3.12.6-slim

# تنظیم دایرکتوری کاری
WORKDIR /app

# کپی فایل‌های مورد نیاز
COPY . /app

# نصب وابستگی‌ها
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# باز کردن پورت
# EXPOSE 8000

# فرمان اجرا
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
