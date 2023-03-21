FROM python:3

LABEL org.opencontainers.image.source=https://github.com/K-4U/ha-keepalive
LABEL org.opencontainers.image.description="Home Assistant keep-alive with external hardware"


WORKDIR /app

ADD index.py index.py
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

EXPOSE 8001
ENTRYPOINT ["python3", "index.py"]
