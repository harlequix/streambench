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
docker compose run streambench --media /examples/bbb_sunflower_1080p_30fps_normal.mp4 --csv /results/bbb_30fps.csv --recording /results/bbb_30fps_copy.mp4
```
This will start the benchmarking process for the (local) Big Buck Bunny video.

## General Usage
Streambench requires the following parameters:
```sh
docker compose run streambench <playback_file> <csv_output> <timeout>
```
- `--media`: This can be any file that MPV can play back.
- `--csv`: Output path for the timing information.
- `--recording`: This utilizes MPV to record the played back media for later analysis.


Optional parameter:
- `--playbook`: utilizes a playbook (see playbook generation)
- `--mapping`: defines the mapping between ID's in a playbook and port used for RTP transmission. Expected is a `ID:Port` mapping, e.g. `0:5004` sends playbook ID 0 to port 5004

## Playback of RTP
Since the playback can be anything that MPV can play back, Streambench can also be used to benchmark RTP playbacks. To achieve that, follow these steps:

1. Create a valid SDP file that describes the RTP session.
2. Edit the `compose.yml` to open/forward the corresponding ports to the Streambench container.
3. Run Streambench with the SDP file as input.

## Playbook creation

Playbook creation is done via the preprocessing container provided by `compose.yml`.
`docker compose preprocess <path to media file> <path to playbook output>` creates both a playbook and a valid sdp file in the defined location.

## Contributing
We welcome contributions! Please read our [contributing guidelines](CONTRIBUTING.md) for more details.

