
import csv
import os
import time
import functools
import mpv
import threading
import queue
from dataclasses import dataclass, asdict
from loguru import logger
import sys


@dataclass
class Frame:
    num: int
    frametime: float
    timestamp: float

@dataclass
class RecordingContext:
    duration: int
    signal_flush_to_disk: threading.Event 
    signal_playback_finished: threading.Event
    signal_has_started: threading.Event
    signal_heartbeat: threading.Event
    mpv_ctx: mpv.MpvRenderContext
    player: mpv.MPV
    frame_queue: queue.SimpleQueue
    last_frame: Frame = None
    start_time: float = None
    frame_num: int = 0
    

class Receiver:
    def __init__(self, sdp, csv, recording, loglevel='debug'):
        self.recording = recording
        self.loop = False
        self.logfile = None
        self.duration = 120
        self.sdp = sdp
        self.csv = csv
        self.loglevel = loglevel
        logger.remove()
        logger.add(sys.stderr, level=self.loglevel.upper())

        
    def _trapterm_signal(self, *args):
        self.done.set()
        time.sleep(10)
        os.system('kill -9 %d' % os.getpid())
        
    def _mpv_log_handler(self, *args):
        pass
    
    def start(self):
        logger.info("Starting receiver")
        player = mpv.MPV(loop=self.loop, ytdl=True, log_handler=functools.partial(Receiver._mpv_log_handler, self), loglevel='debug', stream_record=self.recording)
        self.duration = int(self.duration)
        frames = queue.SimpleQueue()
        
        flush_to_disk = threading.Event()
        playback_finished = threading.Event()
        has_started = threading.Event()
        heartbeat = threading.Event()
        
        mpv_ctx = mpv.MpvRenderContext(player, 'sw')
        rec_ctx = RecordingContext(self.duration, flush_to_disk, playback_finished, has_started, heartbeat, mpv_ctx, player, frames)
        mpv_ctx.update_callback = functools.partial(frame_ready,rec_ctx)
        
        t_writer = threading.Thread(target=writer, args=(frames, self.csv, playback_finished))
        t_deadlock = threading.Thread(target=trapdoor, args=(has_started, playback_finished, False))
        t_stuck = threading.Thread(target=trapdoor, args=(heartbeat, playback_finished, True))
        
        t_writer.start()
        t_deadlock.start()
        t_stuck.start()

        player.play(self.sdp)
        playback_finished.wait()
        
        
def frame_ready(context):
    logger.debug(f"Frame ready: {context.frame_num}")
    current_time = time.time()
    if context.last_frame is not None:
        t0 = current_time
        time_since_last_frame = current_time - context.last_frame.timestamp
    else:
        t0 = current_time
        time_since_last_frame = 0
        logger.debug("Starting recording")
        context.signal_has_started.set()
    
    frame = Frame(context.frame_num, time_since_last_frame, current_time - t0)
    logger.debug(f"Frame: {frame}")
    context.frame_queue.put(frame)
    logger.debug("Frame put in queue")
    context.signal_heartbeat.set()
    if frame.timestamp > context.duration:
            logger.info("Recording finished")
            context.signal_flush_to_disk.set()
            context.signal_playback_finished.set()
            context.player.terminate()

    context.last_frame = frame
    context.frame_num += 1
    # context.mpv_ctx.render(skip_rendering=True, block_for_target_time=False)


        
def writer(queue, file, done):
    with open(file, 'w+') as f:
        header = ["num", "timestamp", "frametime"]
        wr = csv.DictWriter(f, fieldnames=header)
        wr.writeheader()
        while not done.is_set():
            frame = queue.get()
            wr.writerow(asdict(frame))
            # print(f'Writing {frame}')
            f.flush()
        while not queue.empty():
            frame = queue.get()
            wr.writerow(asdict(frame))
            # print(f'Writing {frame}')
            f.flush()

def trapdoor(event1, event2, reset, timeout=120):
    time.sleep(timeout)
    if not event1.is_set():
        print("Nothing is happening, trigger exit")
        event2.set()
    elif reset:
        event1.clear()