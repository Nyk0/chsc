#!/bin/bash

/bin/bash /generate-config.sh

sleep 2

/usr/sbin/sshd -D -f /etc/oar/sshd_config
