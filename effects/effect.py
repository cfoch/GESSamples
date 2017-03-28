from gi.repository import Gtk
from gi.repository import GES
from gi.repository import Gst
from gi.repository import GObject
 
import signal
 
video_path = "/home/fabian/Videos/sintel.ogv"
 
def handle_sigint(sig, frame):
    print("Bye!")
    Gtk.main_quit()
 
def busMessageCb(unused_bus, message):
    if message.type == Gst.MessageType.EOS:
        print("EOS: The End")
        Gtk.main_quit()
 
def duration_querier(pipeline):
    print(pipeline.query_position(Gst.Format.TIME))
    return True

def childAddedCb(clip, track_element):
    print(clip)
 
if __name__ == "__main__":
    GObject.threads_init()
    Gst.init(None)
    GES.init()
 
    video_uri = "file://" + video_path
 
    timeline = GES.Timeline.new_audio_video()


    layer = timeline.append_layer()
    layer2 = timeline.append_layer()
 
    asset = GES.UriClipAsset.request_sync(video_uri)
    clip = layer2.add_asset(asset, 0, 0, 5 * Gst.SECOND, GES.TrackType.UNKNOWN)
    print(clip.get_children(False))

    clip2 = layer2.add_asset(asset, 5 * Gst.SECOND, 20 * Gst.SECOND,
        5 * Gst.SECOND, GES.TrackType.VIDEO)



    # pipe = "videoconvert ! videomixer name=mix ! videoconvert name=conv videotestsrc pattern=snow ! shapewipe position=0.5 name=shape  ! videoconvert ! videoscale ! video/x-raw,width=1024,height=768 ! mix. filesrc location=/home/cfoch/Pictures/mask.jpg ! decodebin ! videoconvert ! videoscale ! shape.mask_sink conv."
    pipe = "videoconvert ! agingtv ! videoconvert"

    effect_clip = GES.EffectClip.new(pipe, "audioconvert")
    effect_clip.set_start(0)
    effect_clip.set_duration(10 * Gst.SECOND)
    layer.add_clip(effect_clip)

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
