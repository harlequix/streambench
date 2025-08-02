#!/bin/bash
sudo tcpdump -s 0 -i lo port 5555 -w $2 &
ffmpeg \
    -re \
    -i $1 \
    -c:a copy \
    -vn \
    -f rtp \
    "rtp://127.0.0.1:5555"
