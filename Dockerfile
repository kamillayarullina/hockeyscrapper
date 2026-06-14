FROM python:3.11-slim

WORKDIR /app

# System deps for Playwright
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl wget ca-certificates fonts-liberation libasound2 \
    libatk-bridge2.0-0 libatk1.0-0 libcups2 libdbus-1-3 \
    libdrm2 libgbm1 libglib2.0-0 libnspr4 libnss3 libu2f-udev \
    libvulkan1 libxcomposite1 libxdamage1 libxfixes3 libxkbcommon0 \
    libxrandr2 xdg-utils libwoff1 libopus0 libwebpdemux2 \
    libwebp7 libenchant-2-2 libgudev-1.0-0 libhyphen0 \
    libgles2 libegl1 libevdev2 libgstreamer-plugins-base1.0-0 \
    libgstreamer1.0-0 libgstreamer-gl1.0-0 libopenjp2-7 \
    libmanette-0.2-0 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright Chromium
RUN python -m playwright install chromium && python -m playwright install-deps chromium

COPY . .

EXPOSE 8000

CMD ["python", "-m", "main", "--all"]
