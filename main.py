import argparse
import streambench
import multiprocessing
import signal
import sys
from loguru import logger

def receive(media, csv, recording=None, loglevel="info"):
    """
    Function to receive media streams and log the output.
    :param media: Path to the SDP file.
    :param csv: Path to the CSV file.
    :param recording: Optional path to the recording file.
    :param loglevel: Log level for logging.
    """
    logger.remove()
    logger.add(sys.stdout, level=loglevel.upper())
    
    shutdown_event = multiprocessing.Event()
    
    def handle_sigterm(signum, frame):
        logger.info("SIGTERM received, shutting down gracefully...")
        shutdown_event.set()
        
    signal.signal(signal.SIGTERM, handle_sigterm)
    signal.signal(signal.SIGINT, handle_sigterm)

    receiver = streambench.Receiver(media, csv, recording, shutdown_event, loglevel)
    receiver.start()


def main():
    parser = argparse.ArgumentParser(description="streambench")
    subparsers = parser.add_subparsers(dest="command", required=True)
    receiver_parser = subparsers.add_parser("receive", help="Run the receiver")
    receiver_parser.add_argument("--media", help="Path to the sdp file", required=True)
    receiver_parser.add_argument("--csv", help="Path to the csv file", required=True)
    receiver_parser.add_argument("--recording", help="Path to the recording file", required=False, default=None)
    receiver_parser.add_argument("--loglevel", help="Log level", default="info")
    # parser.add_argument("--playbook", help="Path to the playbook that describes the simulated scenario")
    # parser.add_argument("--mapping", action="append", help="Mapping of the events to the target addresses")
    args = parser.parse_args()
    logger.info(args)

    match args.command:
        case "receive":
            receive(args.media, args.csv, args.recording, args.loglevel)
        case _:
            logger.error("Unknown command")



def parse_mappings(mappings_list):
    mappings = {}
    for mapping in mappings_list:
        key, value = mapping.split(":")
        mappings[int(key)] = int(value)
    return mappings

if __name__ == "__main__":
    main()
