import argparse
import json
import logging
from pprint import pprint
from events import Event
from dataclasses import asdict

def parse_input(input, id=0):
    out = []
    with open(input) as jsonfile:
        jdata = json.load(jsonfile)
        filtered = [x for x in jdata if x["name"] == "Stream" and x["msg"] == "Delivery"]
        for x in filtered:
            print(x)
            start_byte = x["Offset"]
            ev = Event(id=x["ID"], start=x["Time"], start_byte=start_byte, end_byte=start_byte+x["Size"], payload=[], seqnr=0)
            out.append(ev)
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", nargs='+')
    parser.add_argument("--output")
    parser.add_argument("-l", "--log", default="warning")
    args = parser.parse_args()
    logging.basicConfig(level=args.log.upper(),
                        format='%(asctime)s.%(msecs)03d %(levelname)s\t[%(name)s]:\t%(message)s',
                        datefmt='%Y-%m-%d,%H:%M:%S')
    log = logging.getLogger(__name__)
    log.debug("input: %s", args.inputs)
    log.debug("output: %s", args.output)
    data = []
    for id, file in enumerate(args.inputs):
        dp = parse_input(file, id)
        data += [asdict(x) for x in dp]
    data = sorted(data, key=lambda d: d['start'])
    with open(args.output, 'w') as jsonfile:
        json.dump(data, jsonfile, indent=4)


if __name__ == '__main__':
    main()
