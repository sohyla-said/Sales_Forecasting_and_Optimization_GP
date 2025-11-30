# Use official python image
FROM python:3.11-slim

# Install system dependencies required for ML models
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# set working directory
WORKDIR /app

# copy requirements.txt file
COPY requirements.txt /app/

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# copy the rest of the project
COPY . /app/

# expose port
EXPOSE 8000

# Set default command
CMD ["uvicorn", "Server.main_api:app", "--host", "0.0.0.0", "--port", "8000"]
