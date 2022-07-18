FROM python:latest

RUN echo "deb http://deb.debian.org/debian bullseye-backports main contrib non-free" >> /etc/apt/sources.list \
  && apt-get update && apt-get install -y vim.tiny \
  && pip install --upgrade pip && pip install kubernetes

COPY controller.py ./

CMD exec /bin/bash -c "trap : TERM INT; sleep infinity & wait"
