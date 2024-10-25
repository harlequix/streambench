#!/bin/bash


if [ ! -f bbb_sunflower_1080p_30fps_normal.mp4 ]; then
    if [ ! -f bbb_sunflower_1080p_30fps_normal.mp4.zip ]; then
        wget https://download.blender.org/demo/movies/BBB/bbb_sunflower_1080p_30fps_normal.mp4.zip
    fi
    unzip bbb_sunflower_1080p_30fps_normal.mp4.zip
fi
