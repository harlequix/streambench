#!/bin/bash
sudo tcpdump -s 0 -i lo port 5004 -w $2 &
sudo tcpdump -s 0 -i lo port 7005 -w $3 &
pid=$!
sleep 2
ffmpeg -re -i $1 -an  -c:v copy -f rtp "rtp://127.0.0.1:5004" -acodec libmp3lame -vn -sdp_file $4.sdp -f rtp "rtp://127.0.0.1:7005"
sleep 2
kill $pid
