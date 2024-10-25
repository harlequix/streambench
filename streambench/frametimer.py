#!/usr/bin/env python3

import sys
import time
import ctypes
import os

import mpv
import click
import csv
import threading
import queue
import time
import signal

def get_process_address(_, name):
    address = GLX.glXGetProcAddress(name.decode("utf-8"))
    return ctypes.cast(address, ctypes.c_void_p).value

def mpv_log(loglevel, component, message):
    # print('[{}] {}: {}'.format(loglevel, component, message))
    pass

@click.command()
@click.argument('filename')
@click.argument("logfile")
@click.argument("duration")
@click.option('--loop', default=False)
@click.option('--output', default="out.mp4")
def frametimer(filename, loop, logfile, duration, output):
    p = mpv.MPV(loop=loop, ytdl=True, log_handler=mpv_log, loglevel='debug', stream_record=output)
    duration = int(duration)
    frame_num = 0
    last_frame_time = None
    t0 = time.time()
    frames = queue.SimpleQueue()
    done = threading.Event()
    pb = threading.Event()
    active = threading.Event()
    thread = threading.Thread(target=writer, args=(frames, logfile, done))
    thread.start()
    deadlock = threading.Thread(target=trapdoor, args=(active, pb, False))
    deadlock.start()
    heartbeat = threading.Event()
    stuck = threading.Thread(target=trapdoor, args=(heartbeat, pb, True))
    stuck.start()
    def trapterm(*args):
        nonlocal done
        print("Catching sigterm")
        done.set()
        time.sleep(10)
        print("Exiting")
        os.system('kill -9 %d' % os.getpid())
    signal.signal(signal.SIGTERM, trapterm)
    last_time_update = 0
    
    def frame_ready():
        # print("Frame ready")
        nonlocal frame_num, last_frame_time, ctx, t0, frames, p, pb, active
        current_time = time.time()
        if last_frame_time is not None:
            frame = {}
            frame["num"] = frame_num
            frame["frametime"] = current_time - last_frame_time
            frame["timestamp"] = current_time - t0
            frames.put(frame)
            heartbeat.set()
            # print(f'[{frame["timestamp"]}]Frame {frame_num} @ {(current_time - last_frame_time)*1000:.3f} ms')
            if frame["timestamp"] > duration:
                # with open(logfile, "w+") as csvfile:
                #     writer = csv.DictWriter(csvfile, fieldnames=frame.keys())
                #     writer.writeheader()
                #     writer.writerows(frames)
                done.set()
                pb.set()
                p.terminate()
        else:
            t0 = time.time()
            active.set()
        last_frame_time = current_time
        frame_num += 1
        ctx.render(skip_rendering=True, block_for_target_time=False)

    ctx = mpv.MpvRenderContext(p, 'sw')
    ctx.update_cb = frame_ready
    p.play(filename)
    # p.wait_for_playback()
    pb.wait()
    # p.terminate()
    print('Exiting.')
    os.system('kill %d' % os.getpid())




def writer(queue, file, done):
    with open(file, 'w+') as f:
        header = ["num", "timestamp", "frametime"]
        wr = csv.DictWriter(f, fieldnames=header)
        wr.writeheader()
        while not done.is_set():
            frame = queue.get()
            wr.writerow(frame)
            # print(f'Writing {frame}')
            f.flush()
        while not queue.empty():
            frame = queue.get()
            wr.writerow(frame)
            # print(f'Writing {frame}')
            f.flush()

def trapdoor(event1, event2, reset, timeout=120):
    time.sleep(timeout)
    if not event1.is_set():
        print("Nothing is happening, trigger exit")
        event2.set()
    elif reset:
        event1.clear()

if __name__ == '__main__':
    frametimer()
