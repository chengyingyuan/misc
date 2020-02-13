#!/usr/bin/env python3

# Python 2/3 compatibility.
from __future__ import print_function

import sys
import os
import time
import signal
from Xlib import X, XK, display
from Xlib.ext import record
from Xlib.protocol import rq
from ewmh import EWMH

signal.signal(signal.SIGTERM, lambda a,b:sys.exit(1))
signal.signal(signal.SIGINT, lambda a,b:sys.exit(1))

def lookup_keysym(keysym):
    for name in dir(XK):
        if name[:3] == "XK_" and getattr(XK, name) == keysym:
            return name[3:]
    return "[%d]" % keysym

ewmh = EWMH()
#local_dpy = display.Display()
local_dpy = ewmh.display
record_dpy = display.Display()

tracked_syms = [XK.XK_Control_L, XK.XK_Shift_L, XK.XK_d]
tracked_codes = [local_dpy.keysym_to_keycode(v) for v in tracked_syms]
tracked_keys = {v:False for v in tracked_codes}
tracked_names = {v:lookup_keysym(local_dpy.keycode_to_keysym(v,0)) for v in tracked_codes}


def toggle_desktop():
    i = ewmh.getCurrentDesktop()
    target = 0 if i > 0 else 1
    ewmh.setCurrentDesktop(target)
    ewmh.display.flush()

def track_key(keycode, evtype):
    global tracked_keys
    if keycode not in tracked_keys:
        return
    if evtype == X.KeyPress:
        print('Key {} pressed'.format(tracked_names[keycode]))
        tracked_keys[keycode] = True
        toggle = True
        for pressed in tracked_keys.values():
            if not pressed:
                toggle = False
        if toggle:
            toggle_desktop()
    elif evtype == X.KeyRelease:
        print('Key {} released'.format(tracked_names[keycode]))
        tracked_keys[keycode] = False

def record_callback(reply):
    if reply.category != record.FromServer:
        return
    if reply.client_swapped:
        print("* received swapped protocol data, cowardly ignored")
        return
    if not len(reply.data) or reply.data[0] < 2:
        # not an event
        return
    data = reply.data
    while len(data):
        event, data = rq.EventField(None).parse_binary_value(data, record_dpy.display, None, None)
        #print('Event:', event)
        if event.type in [X.KeyPress, X.KeyRelease]:
            keycode = event.detail
            track_key(keycode, event.type)
            # pr = event.type == X.KeyPress and "Press" or "Release"
            # keysym = local_dpy.keycode_to_keysym(event.detail, 0)
            # if not keysym:
            #     print("KeyCode%s" % pr, event.detail)
            # else:
            #     keynam = lookup_keysym(keysym)
            #     print("KeyStr%s" % pr, keynam)
            #     track_key(keynam, event.type)

            # if event.type == X.KeyPress and keysym == XK.XK_Escape:
            #     local_dpy.record_disable_context(ctx)
            #     local_dpy.flush()
            #     return
        # elif event.type == X.ButtonPress:
        #     print("ButtonPress", event.detail)
        #     pass
        # elif event.type == X.ButtonRelease:
        #     print("ButtonRelease", event.detail)
        #     pass
        # elif event.type == X.MotionNotify:
        #     print("MotionNotify", event.root_x, event.root_y)
        #     pass


# Check if the extension is present
if not record_dpy.has_extension("RECORD"):
    print("RECORD extension not found")
    sys.exit(1)
r = record_dpy.record_get_version(0, 0)
print("RECORD extension version %d.%d" % (r.major_version, r.minor_version))

# Create a recording context; we only want key and mouse events
ctx = record_dpy.record_create_context(
        0,
        [record.AllClients],
        [{
                'core_requests': (0, 0),
                'core_replies': (0, 0),
                'ext_requests': (0, 0, 0, 0),
                'ext_replies': (0, 0, 0, 0),
                'delivered_events': (0, 0),
                'device_events': (X.KeyPress, X.KeyRelease), # X.ButtonPress, MotionNotify
                'errors': (0, 0),
                'client_started': False,
                'client_died': False,
        }])

# Enable the context; this only returns after a call to record_disable_context,
# while calling the callback function in the meantime
record_dpy.record_enable_context(ctx, record_callback)

# Finally free the context
record_dpy.record_free_context(ctx)
