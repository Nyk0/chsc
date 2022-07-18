#!/bin/bash

/bin/bash /generate-config.sh

/usr/sbin/sshd -D -f /etc/oar/sshd_config
