FROM python:3.13-slim

WORKDIR /app

RUN apt update
RUN apt install git

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY utils .
COPY speechtotext.py .

CMD [ "python", "./speechtotext.py" ]
