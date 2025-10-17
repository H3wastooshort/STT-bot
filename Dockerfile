##install pip packages
FROM python:3.13-slim AS builder
WORKDIR /app

#install git for pip
RUN apt update
RUN apt install git -y

#make venv
ENV VIRTUAL_ENV=/app/.venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

#install packages into venv
COPY requirements.txt ./
RUN pip install --index-url=https://download.pytorch.org/whl/cpu --extra-index-url=https://pypi.org/simple --no-cache-dir -r requirements.txt && pip uninstall triton -y


##build final image
FROM python:3.13-slim
WORKDIR /app

#install ffmpeg
RUN apt update
RUN apt install ffmpeg -y
RUN apt clean && \
  rm -rf /var/lib/apt/lists/*

#copy python dependencies
COPY --from=builder /app/.venv /app/.venv
#copy application
COPY utils ./utils
COPY speechtotext.py ./

#set venv
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

#run bot
SHELL ["/bin/sh", "-c"]
CMD . $VIRTUAL_ENV/bin/activate && exec python speechtotext.py
