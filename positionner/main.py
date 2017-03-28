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
 
    asset = GES.UriClipAsset.request_sync(video_uri)
    clip = layer.add_asset(asset, 0, 0, asset.get_duration(), GES.TrackType.UNKNOWN)
    print(clip.get_children(False))
    source = clip.get_children(False)[1]
    source.set_child_property("zorder", -1)
    source.set_child_property("posx", 900)

    asset2 = GES.UriClipAsset.request_sync(video_uri)
    clip2 = layer.add_asset(asset2, 0, 20 *  Gst.SECOND, asset2.get_duration(), GES.TrackType.VIDEO)
    source2 = clip2.get_children(False)[0]
    source2.set_child_property("zorder", 1)

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
