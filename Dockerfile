# Chọn Python image nhỏ gọn
FROM python:3.11.7-slim

WORKDIR /app

COPY requirement.txt .

RUN pip install --no-cache-dir -r requirement.txt

COPY . .

EXPOSE 8000

# Chạy file run.py (chạy uvicorn)
CMD ["python", "run.py"]
