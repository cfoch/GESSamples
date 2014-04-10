import signal

from gi.repository import Gtk
from gi.repository import GES
from gi.repository import Gst
from gi.repository import GObject

path = "/home/cfoch/Pictures/Trash/bandas/%d.jpg"
width = 500
height = 360

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

    video_uri = "multifile://" + path

    # Setting Timeline.
    timeline = GES.Timeline()

    # Setting Track.
    imgtrack = GES.VideoTrack.new()
    timeline.add_track(imgtrack)

    layer = GES.Layer.new()
    timeline.add_layer(layer)

    asset = GES.UriClipAsset.request_sync(video_uri)    

    clip = layer.add_asset(asset, 0, 0, 15 * Gst.SECOND, GES.TrackType.VIDEO)
    source = clip.get_children(False)[0]
    source.set_framerate(1, 1)

    imgtrack.set_restriction_caps(Gst.caps_from_string("video/x-raw, height=320, width=400"))
    # timeline.commit()

    pipeline = GES.Pipeline.new()
    pipeline.set_timeline(timeline)

    pipeline.set_state(Gst.State.PLAYING)

    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", busMessageCb)
    GObject.timeout_add(300, duration_querier, pipeline)
    signal.signal(signal.SIGINT, handle_sigint)

    Gtk.main()

"""
 gst-launch-1.0 multifilesrc location="%d.png" index=0 caps="image/png,framerate=1/1" ! pngdec ! videoconvert ! videorate ! xvimagesink
"""
