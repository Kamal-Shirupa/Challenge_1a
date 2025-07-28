FROM python:3.11

WORKDIR /app

COPY main.py .
COPY requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt

CMD ["python", "main.py"]
