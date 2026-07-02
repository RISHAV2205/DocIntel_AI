# -------------------------------
# Base Image
# -------------------------------
FROM python:3.12-slim

# -------------------------------
# Prevent Python from creating .pyc files
# and enable real-time logs
# -------------------------------
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# -------------------------------
# Install system dependencies
# -------------------------------
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# -------------------------------
# Working Directory
# -------------------------------
WORKDIR /app

# -------------------------------
# Install Python dependencies
# -------------------------------
COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# -------------------------------
# Copy Project
# -------------------------------
COPY . .

# -------------------------------
# Expose FastAPI Port
# -------------------------------
EXPOSE 8000

# -------------------------------
# Start FastAPI
# -------------------------------
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]