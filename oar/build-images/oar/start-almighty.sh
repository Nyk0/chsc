#!/bin/bash

/bin/bash /generate-config.sh

oar-database --create --db-admin-user root --db-admin-pass azerty --db-ro-user oar_ro --db-ro-pass azerty --conf /etc/oar/oar.conf

/usr/sbin/Almighty
