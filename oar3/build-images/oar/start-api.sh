#!/bin/bash

/bin/bash /generate-config.sh

/usr/sbin/apache2ctl -D FOREGROUND
