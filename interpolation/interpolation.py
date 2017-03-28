from gi.repository import Gtk
from gi.repository import GES
from gi.repository import Gst
from gi.repository import GObject

from gi.repository import GstController

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

def controlSourceChangedValueCb(control_source, value):
    print("changed", value)

def controlSourceAddedValueCb(control_source, value):
    print("set", value)

def controlBindingAddedCb(track_element, binding):
    csource = binding.props.control_source
    csource.connect("value-changed", controlSourceChangedValueCb)
    csource.connect("value-added", controlSourceAddedValueCb)
    csource.set(2 * Gst.SECOND, 0.1)
    csource.set(2 * Gst.SECOND, 0.7)

def trackElementAddedCb(clip, track_element):
    print("child-added ", track_element, " to ", clip)
    if not isinstance(track_element, GES.VideoUriSource):
        return
    track_element.connect("control-binding-added", controlBindingAddedCb)
    control_source = GstController.InterpolationControlSource()
    control_source.props.mode = GstController.InterpolationMode.LINEAR
    track_element.set_control_source(control_source, "alpha", "direct")

def trackElementRemovedCb(clip, track_element):
    print("child-removed ", track_element, " from ", clip)

# def groupAddedCb(timeline, group):
#     print("group-added", group)

def clipAddedCb(layer, clip):
    print("clip-added", clip)
    clip.connect("child-added", trackElementAddedCb)
    clip.connect("child-removed", trackElementRemovedCb)

def clipRemovedCb(layer, clip):
    print("clip-removed", clip)
 
if __name__ == "__main__":
    GObject.threads_init()
    Gst.init(None)
    GES.init()
 
    video_uri = "file://" + video_path
 
    timeline = GES.Timeline.new_audio_video()
    # timeline.connect("group-added", groupAddedCb)

    layer1 = timeline.append_layer()
    layer2 = timeline.append_layer()

    for layer in timeline.get_layers():
        layer.connect("clip-added", clipAddedCb)
        layer.connect("clip-removed", clipRemovedCb)
 
    asset = GES.UriClipAsset.request_sync(video_uri)
    uri_clip = layer1.add_asset(asset, 0, 0, asset.get_duration(), GES.TrackType.UNKNOWN)
    test_clip = GES.TestClip()
    test_clip.set_duration(uri_clip.get_duration())
    test_clip.set_inpoint(0)
    test_clip.set_start(0)
    test_clip.set_mute(True)
    test_clip.set_vpattern(GES.VideoTestPattern.GREEN)
    layer2.add_clip(test_clip)
    from IPython import embed
    embed()

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
