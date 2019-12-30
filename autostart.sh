#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

while [[ "$#" -gt 0 ]]; do case $1 in
  -t|--temp) echo "Starting temperature monitor:"; tmux new-session -d -s temp_report 'cd '$DIR' && /usr/bin/python3 '$DIR'/temp.py; exec bash -i';;
  -r|--reply) echo "Starting email listener and reply bot:"; tmux new-session -d -s temp_listener 'cd '$DIR' && /usr/bin/python3 '$DIR'/listener.py; exec bash -i';;
  -l|--logger) echo "Starting logger:"; tmux new-session -d -s weather_log 'cd '$DIR' && /usr/bin/python3 '$DIR'/log.py; exec bash -i';;
  -w|--web) echo "Starting webpage:"; tmux new-session -d -s temp_web 'cd '$DIR'/web && sudo /usr/bin/python3 '$DIR'/web/tempweb.py; exec bash -i';;
  *) echo "Unknown parameter passed: $1"; exit 1;;
esac; shift; done
