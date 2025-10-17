#install pip packages
FROM python:3.13-slim AS builder

WORKDIR /app

RUN apt update
RUN apt install git -y

#install packages into user folder
COPY requirements.txt ./
RUN pip install --user --no-cache-dir -r requirements.txt

#build final image
FROM python:3.13-slim

COPY --from=builder /root/.local /root/.local #copy python dependencies
COPY utils speechtotext.py . #copy application

CMD [ "python", "./speechtotext.py" ]
