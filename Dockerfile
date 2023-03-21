FROM python:3

WORKDIR /app

ADD index.py index.py
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

EXPOSE 8001
ENTRYPOINT ["python3", "index.py"]
