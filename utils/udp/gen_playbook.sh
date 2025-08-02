#!/bin/bash
./video2pcap.sh $1 /tmp/video.pcap /tmp/audio.pcap $2
./pcap2json.sh /tmp/video.pcap /tmp/video.json
./pcap2json.sh /tmp/audio.pcap /tmp/audio.json
python wjson2playbook.py --inputs /tmp/video.json /tmp/audio.json --output $2 --log debug
