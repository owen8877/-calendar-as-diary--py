rsync --perms --chmod=u+rw,g+rw,o+r --chown $2 \
  config/wakatime.yml config/league_of_graphs.yml config/client_secret.json config/token.pickle \
  $1:~/calendar-as-diary-py/config/
