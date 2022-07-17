FROM debian:latest

RUN echo "deb http://deb.debian.org/debian bullseye-backports main contrib non-free" >> /etc/apt/sources.list \
  && apt-get update \
  && apt-get install -y vim.tiny oar-server oar-server-pgsql oar-node oar-user oar-user-pgsql \
  && apt-get clean

COPY start-almighty.sh ./

CMD exec /bin/bash -c "trap : TERM INT; sleep infinity & wait"
