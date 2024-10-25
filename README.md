# Streambench

Streambench evaluates the performance of video playback via mpv.

## Table of Contents
- [Introduction](#introduction)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [General Usage](#general-usage)
- [Playback of RTP](#playback-of-rtp)
- [Contributing](#contributing)
- [License](#license)

## Introduction
Streambench is a benchmarking tool designed to measure the performance of video playback using the mpv media player. It provides detailed metrics and insights to help optimize video playback performance.

## Installation
The recommended way to use Streambench is through a tested Docker environment, but feel free to test it on a bare metal machine.

```sh
docker compose build
```

## Quick Start
To quickly test Streambench, download the Big Buck Bunny Movie in ./examples (script is provided) and run the following command:
```sh
docker compose run streambench /examples/bbb_sunflower_1080p_30fps_normal.mp4/results/bbb_30fps.csv 120 --output /results/bbb_30fps_copy.mp4
```
This will start the benchmarking process for the Big Buck Bunny video.

## General Usage
Streambench requires the following parameters:
```sh
docker compose run streambench <playback_file> <csv_output> <timeout>
```
- `<playback_file>`: This can be any file that MPV can play back.
- `<csv_output>`: Output path for the timing information.
- `<timeout>`: Maximum time that Streambench should record the playback in seconds.

Optional parameter:
```sh
--output <recording_path>
```
This utilizes MPV to record the played back media for later analysis.

## Playback of RTP
Since the playback can be anything that MPV can play back, Streambench can also be used to benchmark RTP playbacks. To achieve that, follow these steps:

1. Create a valid SDP file that describes the RTP session.
2. Edit the `compose.yml` to open/forward the corresponding ports to the Streambench container.
3. Run Streambench with the SDP file as input.

## Contributing
We welcome contributions! Please read our [contributing guidelines](CONTRIBUTING.md) for more details.

