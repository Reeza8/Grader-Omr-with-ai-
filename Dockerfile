# مرحله اول: نصب ابزارهای لازم برای ساخت
FROM python:3.12-slim AS builder

# نصب ابزارهای ضروری برای ساخت
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# تنظیم دایرکتوری کاری
WORKDIR /app

# کپی کردن و نصب وابستگی‌ها
COPY requirements.txt .
RUN pip install -r requirements.txt

# مرحله دوم: ایجاد ایمیج سبک برای اجرای نهایی
FROM python:3.12-slim AS final

# نصب فقط وابستگی‌های مورد نیاز برای اجرای نهایی
RUN apt-get update && apt-get install -y \
    libpq-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# تنظیم دایرکتوری کاری
WORKDIR /app

# کپی وابستگی‌های نصب شده از مرحله اول
COPY --from=builder /install /usr/local

# کپی فایل‌های پروژه
COPY . .




# فرمان اجرای اپلیکیشن
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
