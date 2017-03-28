from gi.repository import Gtk
from gi.repository import GES
from gi.repository import Gst
from gi.repository import GObject

from IPython import embed
 
import signal
 
video_path = "/home/cfoch/pitivi-git/dummy-cfoch/simple_ges/sintel_trailer-1080p.ogv"
location = "/home/cfoch/Videos/sequences/%d.jpg"
 
def handle_sigint(sig, frame):
    print("Bye!")
    Gtk.main_quit()
 
def busMessageCb(unused_bus, message):
    if message.type == Gst.MessageType.EOS:
        print("EOS: The End")
        Gtk.main_quit()
 
def duration_querier(pipeline, source):
    print(pipeline.query_position(Gst.Format.TIME))
    return True


 
if __name__ == "__main__":
    GObject.threads_init()
    Gst.init(None)
    GES.init()
 
    timeline = GES.Timeline.new_audio_video()
    layer = timeline.append_layer()

    asset = GES.Asset.request(GES.TitleClip, "my-title-clip")
    print("asset's id: ", asset.props.id)
    clip = layer.add_asset(asset, 0, 0, 5 * Gst.SECOND, GES.TrackType.UNKNOWN)

    source = clip.get_children(False)[0]
    print("set text property: ", source.set_child_property("text", "hola"))



    pipeline = GES.Pipeline()
    pipeline.set_timeline(timeline)
 
    pipeline.set_state(Gst.State.PLAYING)
 
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", busMessageCb)
    GObject.timeout_add(300, duration_querier, pipeline, source)
 
    signal.signal(signal.SIGINT, handle_sigint)
 
    Gtk.main()
