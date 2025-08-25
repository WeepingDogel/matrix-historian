FROM python:3.12.3-slim

# Install locales and curl
RUN apt-get update && apt-get install -y --no-install-recommends \
    locales \
    curl \
    fonts-noto-cjk \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/* \
    && sed -i '/zh_CN.UTF-8/s/^# //g' /etc/locale.gen \
    && locale-gen

# Set environment variables
ENV LANG=zh_CN.UTF-8 \
    LANGUAGE=zh_CN:zh \
    LC_ALL=zh_CN.UTF-8 \
    PYTHONPATH=/app

WORKDIR /app

RUN pip install --no-cache-dir \
    streamlit==1.45.0 \
    pandas==2.2.3 \
    requests==2.32.3 \
    plotly==5.20.0 \
    humanize==4.12.3 \
    wordcloud==1.9.3 \
    networkx==2.8.8 \
    matplotlib==3.8.0 \
    scipy==1.12.0


COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app/webui/main.py", "--server.port=8501", "--server.address=0.0.0.0"]

