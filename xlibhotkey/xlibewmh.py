#!/usr/bin/env python3
#
# https://ewmh.readthedocs.io/en/latest/ewmh.html
#
# Ref. wmctrl
#

from Xlib import display,X
from ewmh import EWMH
import time
import uinput


ewmh = EWMH()
uevents = [uinput.KEY_LEFTCTRL, uinput.KEY_LEFTALT, uinput.KEY_ENTER]
udevice = uinput.Device(uevents)


def send_uevents():
    for ue in uevents:
        udevice.emit(ue, 1)
        time.sleep(0.02)
    for ue in uevents:
        udevice.emit(ue, 0)
        time.sleep(0.01)

def list_windows():
    wins = ewmh.getClientList()
    for w in wins:
        wpid = ewmh.getWmPid(w)
        wname = ewmh.getWmName(w)
        #wname = w.get_wm_name()
        wcls = w.get_wm_class()
        print(wpid, ':', wname, ':', wcls)
 
def find_window(key):
    wins = ewmh.getClientList()
    for w in wins:
        wpid = ewmh.getWmPid(w)
        wname = ewmh.getWmName(w)
        #wname = w.get_wm_name()
        wcls = w.get_wm_class()
        #print(wpid, ':', wname, ':', wcls)
        if wcls and key in wcls[1]:
            print('Found window:', wcls)
            return w
    return None

def focus_window(w):
    print('Activiate window:', w)
    #w.set_input_focus(X.RevertToParent, X.CurrentTime)
    #w.configure(stack_mode=X.Above)
    #ewmh.setProperty('_NET_ACTIVE_WINDOW', w)
    ewmh.setActiveWindow(w)
    ewmh.display.flush()

def blur_window(w):
    print('Deactviate window:', w)
    ewmh.setWmState(w, 1, '_NET_WM_STATE_HIDDEN','_NET_WM_STATE_BELOW')
    ewmh.display.flush()

if __name__ == '__main__':
    list_windows()
    filter = 'Gnome-terminal' # 'chrome'
    w = find_window(filter)
    if w:
        #print('Found, actions:', ewmh.getWmAllowedActions(w, True))
        blur_window(w)

