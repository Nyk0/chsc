FROM debian:latest

RUN echo "deb http://deb.debian.org/debian bullseye-backports main contrib non-free" >> /etc/apt/sources.list \
  && apt-get update \
  && apt-get install -y oar-server oar-server-pgsql oar-node oar-user oar-user-pgsql \
  less vim.tiny netcat \
  && mkdir -p /run/sshd \
  && apt-get clean

COPY start-almighty.sh start-node.sh generate-config.sh register.sh ./

CMD exec /bin/bash -c "trap : TERM INT; sleep infinity & wait"
