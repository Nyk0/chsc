#!/bin/bash

/bin/bash /generate-config.sh

sleep 5

oar-database --create --db-admin-user root --db-admin-pass azerty --db-ro-user oar_ro --db-ro-pass azerty --conf /etc/oar/oar.conf

sleep 2

oarproperty -a cpu -c -a host

sleep 2

/usr/sbin/Almighty
