#!/bin/bash
set -e

# Path to SLAPD
SLAPD_BIN="/usr/sbin/slapd"
SLAPD_CONF="ldap:/// ldapi:///"
SLAPD_USER="openldap"
SLAPD_GROUP="openldap"

echo "Initial slapd start to load data..."
$SLAPD_BIN -h "$SLAPD_CONF" -u $SLAPD_USER -g $SLAPD_GROUP

# Wait for slapd to start
MAX_RETRIES=15
COUNT=0
until ldapsearch -x -H ldap://localhost -s base -b "" > /dev/null 2>&1 || [ $COUNT -eq $MAX_RETRIES ]; do
    echo "Waiting for slapd to start... ($COUNT/$MAX_RETRIES)"
    sleep 2
    ((COUNT++))
done

if [ $COUNT -eq $MAX_RETRIES ]; then
    echo "Slapd failed to start in time for data population."
    # We'll try to continue anyway, maybe it's just really slow
fi

# Load the data if it exists
if [ -f /tmp/data.ldif ]; then
    echo "Loading mock data into LDAP..."
    ldapadd -c -x -D "cn=admin,dc=shadownet,dc=local" -w admin -f /tmp/data.ldif || echo "Some entries might already exist or failed."
fi

# Stop the background slapd
echo "Stopping background slapd..."
PID_FILE="/var/run/slapd/slapd.pid"
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    kill $PID
    # Wait for it to stop
    while kill -0 $PID 2>/dev/null; do
        sleep 1
    done
else
    pkill slapd || true
    sleep 2
fi

# Now exec slapd in foreground for supervisor
echo "Starting slapd in foreground for supervisor..."
exec $SLAPD_BIN -d 0 -h "$SLAPD_CONF" -u $SLAPD_USER -g $SLAPD_GROUP
