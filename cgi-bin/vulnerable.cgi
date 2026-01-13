#!/usr/bin/env bash
echo "Content-Type: text/plain"
echo ""
echo "ShadowNet Shellshock Vulnerable Gateway"
echo "========================================"
printenv | while read -r line; do
    echo "ShadowNet CGI Debug: $line"
done
echo "System Uptime: $(uptime)"
