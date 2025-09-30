# Sử dụng Python image chính thức
FROM python:3.11-slim

# Đặt thư mục làm việc
WORKDIR /app

# Copy file requirements
COPY requirements.txt .

# Cài dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ source code vào container
COPY . .

# Expose cổng FastAPI
EXPOSE 8000

# Chạy app bằng uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
