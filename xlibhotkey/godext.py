#!/usr/bin/env python3

from Xlib.display import Display
from Xlib import X, XK
import sys
import signal 
import time

# Use display.keysym_to_keycode(XK_...) get keycode
HOT_KEYSYMS = [XK.XK_Control_L, XK.XK_Shift_L, XK.XK_d]
HOT_KEYCODES = {}
display = None
root = None

def lookup_keysym(keysym):
    for name in dir(XK):
        if name[:3] == "XK_" and getattr(XK, name) == keysym:
            return name[3:]
    return "[%d]" % keysym

def handle_event(event):
    pr = event.type == X.KeyPress and "Press" or "Release"
    keycode = event.detail
    keysym = display.keycode_to_keysym(keycode, 0)
    if not keysym:
        print("KeyCode%s" % pr, event.detail)
    else:
        keynam = lookup_keysym(keysym)
        print("KeyStr%s" % pr, keynam)
    if keycode in HOT_KEYCODES:
        HOT_KEYCODES[keycode] = True if event.type == X.KeyPress else False
        print(HOT_KEYCODES)
        for pressed in HOT_KEYCODES.values():
            if not pressed:
                return
        print("Trigger!!!!")

def main():
    # current display
    global display, root
    display = Display()
    root = display.screen().root

    # we tell the X server we want to catch keyPress event
    root.change_attributes(event_mask = X.KeyPressMask|X.KeyReleaseMask)
    # just grab the "1"-key for now
    # key, modifiers, owner_events, pointer_mode, keyboard_mode, onerror=None
    for keysym in HOT_KEYSYMS:
        keycode = display.keysym_to_keycode(keysym)
        root.grab_key(keycode, 0, True, X.GrabModeSync, X.GrabModeSync)
        HOT_KEYCODES[keycode] = False

    signal.signal(signal.SIGTERM, lambda a,b:sys.exit(1))
    signal.signal(signal.SIGINT, lambda a,b:sys.exit(1))
    #signal.signal(signal.SIGALRM, lambda a,b:sys.exit(1))
    #signal.alarm(10)
    while True:
        event = display.next_event()
        handle_event(event)
        display.allow_events(X.AsyncKeyboard, X.CurrentTime)            

if __name__ == '__main__':
    main()
