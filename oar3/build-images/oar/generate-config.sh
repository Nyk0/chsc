#!/bin/bash

cat << EOF > /etc/oar/oar.conf
DB_HOSTNAME="$PG_HOST"
DB_PORT="5432"
DB_BASE_NAME="$PG_OAR_BASE_NAME"
DB_BASE_LOGIN="$PG_OAR_BASE_USERNAME"
DB_BASE_PASSWD="$PG_OAR_BASE_USERPASS"
DB_BASE_LOGIN_RO="$PG_OAR_BASE_USERNAME_RO"
DB_BASE_PASSWD_RO="$PG_OAR_BASE_USERPASS_RO"
SERVER_HOSTNAME="$OAR_SERVER_HOSTNAME"
SERVER_PORT="6666"
OARSUB_DEFAULT_RESOURCES="/resource_id=1"
OARSUB_NODES_RESOURCES="network_address"
OARSUB_FORCE_JOB_KEY="no"
LOG_LEVEL="2"
LOG_CATEGORIES="all"
OAREXEC_DEBUG_MODE="0"
OAR_RUNTIME_DIRECTORY="/var/lib/oar"
LOG_FILE="/var/log/oar.log"
DEPLOY_HOSTNAME="127.0.0.1"
COSYSTEM_HOSTNAME="127.0.0.1"
DETACH_JOB_FROM_SERVER="1"
OPENSSH_CMD="/usr/bin/ssh -p 6667"
TAKTUK_CMD="/usr/bin/taktuk -t 30 -s"
FINAUD_FREQUENCY="300"
PINGCHECKER_SENTINELLE_SCRIPT_COMMAND="/usr/local/lib/oar/sentinelle.pl -t 30 -w 20"
SCHEDULER_TIMEOUT="30"
SCHEDULER_JOB_SECURITY_TIME="60"
SCHEDULER_GANTT_HOLE_MINIMUM_TIME="300"
SCHEDULER_RESOURCE_ORDER="scheduler_priority ASC, state_num ASC, available_upto DESC, suspended_jobs ASC, network_address ASC, resource_id ASC"
SCHEDULER_PRIORITY_HIERARCHY_ORDER="network_address/resource_id"
SCHEDULER_AVAILABLE_SUSPENDED_RESOURCE_TYPE="default"
HIERARCHY_LABELS="resource_id,network_address,cpu"
SCHEDULER_FAIRSHARING_MAX_JOB_PER_USER=30
ENERGY_SAVING_INTERNAL="no"
JOB_RESOURCE_MANAGER_PROPERTY_DB_FIELD="cpuset"
JOB_RESOURCE_MANAGER_FILE="/etc/oar/job_resource_manager_cgroups.pl"
CPUSET_PATH="/oar"
OARSH_OARSTAT_CMD="/usr/local/bin/oarstat"
OPENSSH_OPTSTR="1246ab:c:e:fgi:kl:m:no:p:qstvxACD:E:F:GI:KL:MNO:PQ:R:S:TVw:W:XYy"
OPENSSH_OPTSTR_FILTERED="1246b:c:e:fgkm:nqstvxCD:KL:MNO:PQ:R:S:TVW:XYy"
OARSH_OPENSSH_DEFAULT_OPTIONS="-oProxyCommand=none -oPermitLocalCommand=no -oUserKnownHostsFile=/var/lib/oar/.ssh/known_hosts"
OARSTAT_DEFAULT_OUTPUT_FORMAT=2
EOF
