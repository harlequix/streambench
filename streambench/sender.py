from loguru import logger
import json
import time
from socket import socket, AF_INET, SOCK_DGRAM

class Sender:
    def __init__(self, playbook, mappings, duration = 120):
        self.playbook = playbook
        self.mappings = mappings
        self.target_ip = "127.0.0.1"
        self.duration = duration
        self.socket = socket(AF_INET, SOCK_DGRAM)

    def send(self):
        with open(self.playbook) as jsonfile:
            events = json.load(jsonfile)
            if self.mappings:
                print(self.mappings)
                print(events[0])
                events = [x for x in events if x["id"] in self.mappings.keys()]
                print(f"{len(events)} events")
                t0 = time.time()
                counter = 0
                for event in events:
                    counter += 1
                    if self.duration > 0 and event["start"] > self.duration:
                        logger.info(f"Skipping event {counter} because it is outside of the timeout")
                        break
                    target = t0 + event["start"]
                    time_to_sleep = target - time.time()
                    if time_to_sleep < 0:
                        time_to_sleep = 0
                    logger.debug(f"sleeping {time_to_sleep} seconds")
                    time.sleep(time_to_sleep)  # <- This is bad. We rely on the accuracy of the OS, which might depend upon kernel etc. Keep track of the error, solution should suffice for now.
                    wakeup = time.time()
                    error = wakeup - target
                    logger.debug(f"Target was {target}, woke up at {wakeup}, error: {error}")
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
                        logger.debug(f"Size of the paylod: {len(payload)}")
                        chunksize = 65000
                        payloads = [payload[x: min(len(payload), x + chunksize)] for x in range(0, len(payload), chunksize)]
                        for p in payloads:
                            sent = self.socket.sendto(p, (self.target_ip, self.mappings[event["id"]]))
                            if sent != len(p):
                                logger.error("Not all bytes were sent")
                                break
                        # s.sendto(payload, addr)
                    except BrokenPipeError:
                        print("ERROR ERROR ERROR ERROR")
                        break
        print("Finished Sending")
        return