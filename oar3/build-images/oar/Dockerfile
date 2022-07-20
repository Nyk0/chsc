FROM debian:latest

RUN echo "deb http://deb.debian.org/debian bullseye-backports main contrib non-free" >> /etc/apt/sources.list \
  && apt-get update \
  && apt-get install -y make perl python3 python3-dev python3-pip curl \
    libpq-dev git perl perl-base openssh-client openssh-server libdbi-perl \
    libsort-versions-perl libterm-ui-perl libjson-perl taktuk libdbd-pg-perl \
    perl perl-base libdbi-perl libjson-perl libyaml-perl libwww-perl apache2 \
    libcgi-fast-perl libapache2-mod-wsgi-py3 less vim.tiny netcat git \
  && mkdir -p /run/sshd \
  && apt-get clean \
  && pip install poetry \
  && git clone https://github.com/oar-team/oar3.git

COPY start-almighty.sh start-node.sh generate-config.sh register.sh ./
COPY oar-restful-api.conf /etc/apache2/sites-available/

WORKDIR /oar3

RUN poetry build && pip install dist/*.whl \
  && make PREFIX=/usr/local server-build \
  && make PREFIX=/usr/local server-install \
  && make PREFIX=/usr/local server-setup \
  && make PREFIX=/usr/local user-build \
  && make PREFIX=/usr/local user-install \
  && make PREFIX=/usr/local user-setup \
  && make PREFIX=/usr/local node-build \
  && make PREFIX=/usr/local node-install \
  && make PREFIX=/usr/local node-setup \
  && make PREFIX=/usr/local api-build \
  && make PREFIX=/usr/local api-install \
  && make PREFIX=/usr/local api-setup \
  && a2enmod headers && a2enmod rewrite \
  && a2ensite oar-restful-api.conf

CMD exec /bin/bash -c "trap : TERM INT; sleep infinity & wait"
