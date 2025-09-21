# FROM python:3.12-slim
# WORKDIR /app
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt
# COPY . .
# COPY .env .
# CMD ["python", "manage.py", "runserver"]
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose port
EXPOSE 8000

# Ensure environment variables are loaded
ENV PYTHONUNBUFFERED=1

# Run Django dev server binding to 0.0.0.0
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
