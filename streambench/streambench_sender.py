
#!/usr/bin/env python

from socket import *
import sys
import time
import argparse
import logging
import json
# import bytearray

# s.sendto(file_name,addr)




def sendWithPlaybook(playbook_path, targets, buffersize, args):
    with open(playbook_path) as jsonfile:
        events = json.load(jsonfile)
        if targets:
            events = [x for x in events if x["id"] in targets.keys()]
            t0 = time.time()
            counter = 0
            for event in events:
                counter += 1
                if args.timeout > 0 and event["start"] > args.timeout:
                    log.info(f"Skipping event {counter} because it is outside of the timeout")
                    break
                target = t0 + event["start"]
                time_to_sleep = target - time.time()
                if time_to_sleep < 0:
                    time_to_sleep = 0
                log.debug(f"sleeping {time_to_sleep} seconds")
                time.sleep(time_to_sleep)  # <- This is bad. We rely on the accuracy of the OS, which might depend upon kernel etc. Keep track of the error, solution should suffice for now.
                wakeup = time.time()
                error = wakeup - target
                log.debug(f"Target was {target}, woke up at {wakeup}, error: {error}")
                # log.verbose(event)
                try:
                    payload_s = event["payload"]
                    payload_s = payload_s.replace(":", " ")
                    payload = bytearray.fromhex(payload_s)
                except KeyError as e:
                    print(event)
                    raise e
                except ValueError as e:
                    print(event)
                    raise e
                try:
                    log.debug(f"Size of the paylod: {len(payload)}")
                    chunksize = 65000
                    payloads = [payload[x: min(len(payload), x + chunksize)] for x in range(0, len(payload), chunksize)]
                    for p in payloads:
                        sent = s.sendto(p, targets[event["id"]])
                        if sent != len(p):
                            log.error("Not all bytes were sent")
                            break
                    # s.sendto(payload, addr)
                except BrokenPipeError:
                    print("ERROR ERROR ERROR ERROR")
                    break
    print("Finished Sending")
    return

port = 1234
IP = "127.0.0.1"

parser = argparse.ArgumentParser(description="streambench")

parser.add_argument("--address", help="Address that streambench binds to", default=IP)
parser.add_argument("--port", help="Port that streambench binds to", default=port, type=int, nargs="+")
#parser.add_argument("--root", help="Path to streambench root directory (right now unused)", default="/")
parser.add_argument("--log", "--debug", default="warning",
                    help="Provide logging level. Example --log debug, default=warning")
parser.add_argument("--playbook", required=True, help="Path to the playbook that describes the simulated scenario")
parser.add_argument("--video", help="Path to the video file that should be played")
parser.add_argument("--prints", help="Debugging Prints on or off. If you want print put yes here", default ="no")
parser.add_argument("--streams", help="select the id of streams to play back", type=str,nargs="+", default=[])
parser.add_argument("--streams-per-port", help="select the number of streams to play back to port", type=int, nargs="+", default=[])
parser.add_argument("--timeout", type=int, help="Timeout in seconds for the sender", default=-1)
args = parser.parse_args()
logging.basicConfig(level=args.log.upper(),
                    format='%(asctime)s.%(msecs)03d %(levelname)s\t[%(name)s]:\t%(message)s',
                    datefmt='%Y-%m-%d,%H:%M:%S')
log = logging.getLogger(__name__)

log.info(args)

s = socket(AF_INET, SOCK_DGRAM)
#Default: IP = 127.0.0.1
#Default: port = 1234
buf = 1024 #Buffersize in byte
addrs = [(IP, x) for x in args.port]
file_path = args.video
playbook_path = args.playbook
print_flag = (args.prints == "yes")

assert(len(args.streams) == len(args.port))
targets = {}
for stream, port in zip(args.streams, args.port):
    try:
        targets[int(stream)] = (IP, port)
    except ValueError:
        try:
            for new_stream in stream.split(","):
                targets[int(new_stream)] = (IP,port)
        except Exception as e:
            raise e
log.info("Start with streams")
sendWithPlaybook(playbook_path, targets, buf, args)
