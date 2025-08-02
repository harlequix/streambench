import argparse
import streambench
import multiprocessing
import signal
import sys
from loguru import logger

def main():
    parser = argparse.ArgumentParser(description="streambench")
    parser.add_argument("--media", help="Path to the sdp file", required=True)
    parser.add_argument("--csv", help="Path to the csv file", required=True)
    parser.add_argument("--recording", help="Path to the recording file", required=False, default=None)
    parser.add_argument("--loglevel", help="Log level", default="info")
    parser.add_argument("--playbook", help="Path to the playbook that describes the simulated scenario")
    parser.add_argument("--mapping", action="append", help="Mapping of the events to the target addresses")
    args = parser.parse_args()
    logger.info(args)

    shutdown_event = multiprocessing.Event()

    def handle_sigterm(signum, frame):
        logger.info("SIGTERM received, shutting down gracefully...")
        shutdown_event.set()
        for proc in processes:
            proc.terminate()
        for proc in processes:
            if proc.is_alive():
                proc.kill()
                proc.join()

    signal.signal(signal.SIGTERM, handle_sigterm)
    signal.signal(signal.SIGINT, handle_sigterm)  # Optional: handle Ctrl+C

    receiver = streambench.Receiver(args.media, args.csv, args.recording, shutdown_event, args.loglevel)

    proc_receiver = multiprocessing.Process(target=receiver.start)
    processes = [proc_receiver]

    if args.playbook:
        if not args.mapping:
            logger.error("Mapping is required when using playbook")
            return
        mappings = parse_mappings(args.mapping)
        # sender = streambench.Sender(args.playbook, mappings)
        # proc_sender = multiprocessing.Process(target=sender.send)
        # processes.append(proc_sender)

    for proc in processes:
        proc.start()

    try:
        for proc in processes:
            proc.join()
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received, shutting down...")
        shutdown_event.set()
        for proc in processes:
            proc.join()

def parse_mappings(mappings_list):
    mappings = {}
    for mapping in mappings_list:
        key, value = mapping.split(":")
        mappings[int(key)] = int(value)
    return mappings

if __name__ == "__main__":
    main()
