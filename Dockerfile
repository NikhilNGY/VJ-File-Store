# --- Use a lightweight Python image ---
FROM python:3.11-slim

# --- Set environment variables ---
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# --- Install system dependencies ---
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# --- Set working directory ---
WORKDIR /app

# --- Copy requirements and install dependencies ---
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# --- Copy project files ---
COPY . .

# --- Expose port for web server if using FastAPI/Flask ---
EXPOSE 8080

# --- Default command to run both bot and web server concurrently ---
# Uses asyncio.run to start your async bot and web server in one process
CMD ["python", "-m", "TechVJ.startup"]
