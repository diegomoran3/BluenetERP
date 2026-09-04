#!/bin/bash
# Diagnose LAN access for the ERPNext stack. Run ON the server.
set -e

LAN_IP=$(hostname -I | awk '{print $1}')
echo "LAN IP:     $LAN_IP"

echo ""
echo "Stack:"
docker ps --format '{{.Names}}  {{.Ports}}' | grep bluenet || echo "(no bluenet containers)"

echo ""
echo "Port 8080:"
ss -tlnp 2>/dev/null | grep ':8080' || netstat -tlnp 2>/dev/null | grep ':8080' || echo "not found"

echo ""
echo "Name resolution on this server:"
for name in localhost.local bluenet.local; do
  if getent hosts "$name" >/dev/null 2>&1; then
    echo "  $name -> $(getent hosts "$name")"
  else
    echo "  $name -> NOT RESOLVED"
  fi
done

echo ""
echo "To enable these names on the SERVER itself (for browsing from the server):"
echo "  sudo sh -c 'echo \"127.0.0.1 localhost.local bluenet.local\" >> /etc/hosts'"
echo ""
echo "To enable on every LAN CLIENT, add this line to each client's hosts file:"
echo "  $LAN_IP bluenet.local"
echo "  (Windows: C:\\Windows\\System32\\drivers\\etc\\hosts as admin)"
