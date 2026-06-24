#!/bin/sh
# Render keep-alive script for the free tier.
# Schedule this script to run every 10 minutes from an external cron or uptime monitor.

# Replace this URL with your actual deployed Render app URL.
APP_URL="${APP_URL:-https://msg-cafeteria.onrender.com/api/health/ping}"

if [ -z "$APP_URL" ]; then
  echo "Error: APP_URL is not set. Set APP_URL to your Render app endpoint." >&2
  exit 1
fi

echo "Pinging keep-alive endpoint: $APP_URL"
status=$(curl -o /dev/null -s -w "%{http_code}" "$APP_URL")

if [ "$status" -eq 200 ]; then
  echo "Success: keep-alive ping returned 200."
  exit 0
else
  echo "Warning: keep-alive ping returned status $status." >&2
  exit 2
fi
