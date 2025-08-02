FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y python3 python3-pip libmpv-dev curl ca-certificates ffmpeg tshark sudo tcpdump
RUN ln -s /usr/bin/python3 /usr/bin/python
ADD https://astral.sh/uv/0.4.26/install.sh /uv-installer.sh
RUN chmod +x /uv-installer.sh && /uv-installer.sh && rm /uv-installer.sh
COPY . /app
WORKDIR /app
ENV PATH="/root/.cargo/bin/:$PATH"
RUN uv sync --frozen
# ENTRYPOINT ["uv", "run", "./streambench/frametimer.py"]
ENTRYPOINT ["uv", "run", "main.py"]