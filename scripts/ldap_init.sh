#!/bin/bash

# Start slapd in background
/usr/sbin/slapd -h "ldap:/// ldapi:///" -g openldap -u openldap

# Wait for it to start
sleep 3

# Add the data
ldapadd -x -D "cn=admin,dc=shadownet,dc=local" -w admin -f /tmp/data.ldif || true

# Kill it so supervisor can take over or just let it stay
# Actually, better to have a script that supervisor runs
# For simplicity, we'll use this script as the LDAP program in supervisor
exec /usr/sbin/slapd -d 0 -h "ldap:/// ldapi:///" -g openldap -u openldap
