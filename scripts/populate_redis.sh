#!/bin/bash
# Wait for Redis to be ready
until redis-cli ping > /dev/null 2>&1; do
  echo "Waiting for Redis to start..."
  sleep 1
done

# Populate Redis with mock data
redis-cli set "SYSTEM_VERSION" "v1.4.2-beta"
redis-cli set "FLAG_INTERNAL_PORT_SCAN" "enabled"
redis-cli set "SECRET_ADMIN_TOKEN" "ShadowNet{R3d1s_1s_4lw4ys_0p3n}"
redis-cli hset "user:1001" "username" "admin" "session" "sess_5a2b8c9d0e1f2"
redis-cli hset "user:1002" "username" "guest" "session" "sess_1a2b3c4d5e6f7"
echo "Redis populated."
