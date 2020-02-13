#!/usr/bin/env python3
#
# http://python-xlib.sourceforge.net/doc/html/python-xlib_21.html#SEC20
#

from Xlib import display, X

d = display.Display()
root = d.screen().root

def print_window_hierrarchy(window, indent):
    children = window.query_tree().children
    for w in children:
        name = w.get_wm_name()
        cls = w.get_wm_class()
        attrs = w.get_attributes()
        if attrs.map_state == X.IsViewable:
            print(indent, name, ':', cls)
        print_window_hierrarchy(w, indent+'-')

"""query = root.query_tree()
for c in query.children:
    # returns window name or None
    name = c.get_wm_name()
    cls_name = c.get_wm_class()
    if name:
        print(name, ':', cls_name)
"""

print_window_hierrarchy(root, '-')

