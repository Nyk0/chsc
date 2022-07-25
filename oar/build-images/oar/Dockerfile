FROM debian:latest

RUN echo "deb http://deb.debian.org/debian bullseye-backports main contrib non-free" >> /etc/apt/sources.list \
  && apt-get update \
  && apt-get install -y make perl python3 bzip2 wget g++ gcc vim.tiny \
  oar-server oar-server-pgsql oar-node oar-user oar-user-pgsql pip \
  less vim.tiny postgresql-client taktuk libjson-pp-perl netcat bind9-host \
  && apt-get clean \
  && useradd -u 1000 nico -s /bin/bash \
  && mkdir -p /var/run/sshd \
  && pip install --upgrade pip && pip install kubernetes

COPY start-almighty.sh start-node.sh generate-config.sh register.sh controller.py create-resources.sh ./

CMD exec /bin/bash -c "trap : TERM INT; sleep infinity & wait"
