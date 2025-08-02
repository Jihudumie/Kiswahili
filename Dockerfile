FROM python:3.11-slim

# Add ffmpeg source dependencies na kuinstall
RUN apt update && apt install -y ffmpeg gcc libffi-dev libssl-dev && apt clean

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your bot code
COPY . .

# Run the bot
CMD ["python", "Swahili.py"]
