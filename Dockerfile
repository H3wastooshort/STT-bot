##install pip packages
FROM python:3.13-slim AS builder

WORKDIR /app

RUN apt update
RUN apt install git -y

#install packages into user folder
COPY requirements.txt ./
RUN python -m venv /app/.venv
RUN source /app/.venv/bin/activate && pip install --user --no-cache-dir -r requirements.txt


##build final image
FROM python:3.13-slim

#copy python dependencies
COPY --from=builder /app/.venv /app/.venv
#copy application
COPY utils speechtotext.py docker-entrypoint.sh .

CMD [ "./docker-entrypoint.sh" ]
