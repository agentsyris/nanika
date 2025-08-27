FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY ../../requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install apscheduler

# Copy application code
COPY . /app/

# Run the scheduler
CMD ["python", "scheduler.py"]
