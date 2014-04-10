from gi.repository import Gtk
from gi.repository import GES
from gi.repository import Gst
from gi.repository import GObject

import signal

video_path = "/home/cfoch/Videos/samples/big_buck_bunny_1080p_stereo.ogg"

def handle_sigint(sig, frame):
    print "Bye!"
    Gtk.main_quit()

def busMessageCb(unused_bus, message):
    if message.type == Gst.MessageType.EOS:
        print "EOS: The End"
        Gtk.main_quit()

def duration_querier(pipeline):
    print pipeline.query_position(Gst.Format.TIME)
    return True

if __name__ == "__main__":
    GObject.threads_init()
    Gst.init(None)
    GES.init()

    video_uri = "file://" + video_path

    timeline = GES.Timeline.new_audio_video()
    layer = timeline.append_layer()

    asset_video = GES.UriClipAsset.request_sync(video_uri)
    clip_video = layer.add_asset(asset_video, 0, 0, asset_video.get_duration(), GES.TrackType.UNKNOWN)

    clip_effect = GES.EffectClip.new(
        video_bin_description="videobalance saturation=1.5 hue=+0.5",
        audio_bin_description="audiopanorama panorama=1.0")

    #The effect starts after 3 seconds
    clip_effect.set_start(Gst.SECOND * 3) 
    clip_effect.set_inpoint(0)
    clip_effect.set_duration(asset_video.get_duration())
    clip_video.set_priority(0)
    clip_video.set_priority(1)

    layer.add_clip(clip_effect)
    timeline.commit()

    pipeline = GES.Pipeline()
    pipeline.set_timeline(timeline)

    pipeline.set_state(Gst.State.PLAYING)

    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", busMessageCb)
    GObject.timeout_add(300, duration_querier, pipeline)

    signal.signal(signal.SIGINT, handle_sigint)

    Gtk.main()
