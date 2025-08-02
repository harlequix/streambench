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
        it = 0
        for seqnr, packet in enumerate(jdata):
            udpp = packet["_source"]["layers"]["udp"]
            frame = packet["_source"]["layers"]["frame"]
            payload = udpp["udp.payload"]
            time = float(frame["frame.time_epoch"])
            length = int(udpp["udp.length"])
            
            ev = Event(id=id, payload=payload, start=time, start_byte=it, end_byte=it+length, seqnr=seqnr)
            it += length
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
    fix_timestamp = min([x["start"] for x in data])
    for x in data:
        x["start"] = x["start"] - fix_timestamp
    with open(args.output, 'w') as jsonfile:
        json.dump(data, jsonfile, indent=4)


if __name__ == '__main__':
    main()
