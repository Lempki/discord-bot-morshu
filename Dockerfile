FROM python:3.12-slim
RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg libsodium-dev \
    && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home appuser
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -c "import nltk; nltk.download('averaged_perceptron_tagger_eng', quiet=True); nltk.download('punkt_tab', quiet=True)"
COPY . .
USER appuser
CMD ["python", "bot.py"]
