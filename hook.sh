#!/bin/sh

# Functions
die() { echo "error: $@" 1>&2 ; exit 1; }
confDie() { echo "error: $@ Check the server configuration!" 1>&2 ; exit 2; }
debug() {
  [ "$debug" = "true" ] && echo "debug: $@"
}

# Validate global configuration
[ -z "$SECRET" ] && confDie "SECRET not set."

# Validate Github hook
signature=$(echo -n "$1" | openssl sha1 -hmac "$SECRET" | sed -e 's/^.* //')
[ "sha1=$signature" != "$x_hub_signature" ] && die "bad hook signature: expecting $x_hub_signature and got $signature"

# Validate parameters
payload=$1
[ -z "$payload" ] && die "missing request payload"
payload_type=$(echo $payload | jq type -r)
[ $? != 0 ] && die "bad body format: expecting JSON"
[ ! $payload_type = "object" ] && die "bad body format: expecting JSON object but having $payload_type"

debug "received payload: $payload"

if [ "$x_github_event" = "ping" ]
then
    echo "Pong!"
    exit 0
fi

# Extract values
action=$(echo $payload | jq .action -r)
[ $? != 0 -o "$action" = "null" ] && die "unable to extract 'action' from JSON payload"

# Do something with the payload:
# Here create a simple notification when an issue has been published
if [ "$action" = "push" ]
then
    cd /home/xdroid/calendar-as-diary-py/
    git reset HEAD --hard && git pull -f
    source ~/.bashrc
    micromamba activate calendar-as-diary
    micromamba update -f env.yml
    pm2 restart ecosystem.config.js
fi
