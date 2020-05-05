FROM python:3.7

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

WORKDIR /app
COPY . .

CMD ["python3", "main.py"]
