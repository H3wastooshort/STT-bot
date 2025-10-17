FROM python:3.13-alpine

WORKDIR /app

RUN apk add git

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY utils .
COPY speechtotext.py .

CMD [ "python", "./speechtotext.py" ]
