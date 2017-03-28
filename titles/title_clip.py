from gi.repository import Gtk
from gi.repository import GES
from gi.repository import Gst
from gi.repository import GObject

from IPython import embed
 
import signal
 
y = 0
video_path = "/home/cfoch/pitivi-git/dummy-cfoch/simple_ges/sintel_trailer-1080p.ogv"
 
def handle_sigint(sig, frame):
    print("Bye!")
    Gtk.main_quit()
 
def busMessageCb(unused_bus, message):
    if message.type == Gst.MessageType.EOS:
        print("EOS: The End")
        Gtk.main_quit()
 
def duration_querier(pipeline, source):
    global y
    y -= 1
    print("y: %d " % y)
    source.set_child_property("deltay", y)
    print(pipeline.query_position(Gst.Format.TIME))
    return True

def childAddedCb(clip, track_element):
    print("childAddedCb: ", track_element)

text = "hola\ncomo\n"
 
if __name__ == "__main__":
    GObject.threads_init()
    Gst.init(None)
    GES.init()
 
    timeline = GES.Timeline.new_audio_video()
    layer = timeline.append_layer()
 
    clip = GES.TitleClip()
    clip.connect("child-added", childAddedCb)
    clip.set_duration(5 * Gst.SECOND)
    layer.add_clip(clip)
    # print("children: ", clip.get_children(False))
    # print("text: ", clip.get_children(False)[0].get_child_property("text"))

    source = clip.get_children(False)[0]
    source.set_child_property("text", text)
    timeline.commit()
 
    pipeline = GES.Pipeline()
    pipeline.set_timeline(timeline)
 
    pipeline.set_state(Gst.State.PLAYING)
 
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", busMessageCb)
    GObject.timeout_add(300, duration_querier, pipeline, source)
 
    signal.signal(signal.SIGINT, handle_sigint)
 
    Gtk.main()
