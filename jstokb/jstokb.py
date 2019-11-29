#!/usr/bin/env python3
import pygame
import uinput
import time

JSDEV = 0
FPS = 20 # 20 frames per second

BUTTONS = {
  "TRIANGLE":0, "CIRCLE":1, "CROSS":2, "SQUARE":3,
  "L1":4, "R1":5, "L2":6, "R2":7,
  "SELECT":8, "START":9, "LAXIS":10, "RAXIS":11,
  "MODE":12,
    }
BUTTON_NAMES = { BUTTONS[k]:k for k in BUTTONS.keys() }
BUTTON_MAP = {
  "SELECT": uinput.KEY_ESC,
  "START": uinput.KEY_ENTER,
  "SQUARE": uinput.KEY_LEFT,
  "CIRCLE": uinput.KEY_RIGHT,
  "TRIANGLE": uinput.KEY_UP,
  "CROSS": uinput.KEY_DOWN,
  "LAXIS": uinput.BTN_LEFT,
  "RAXIS": uinput.BTN_RIGHT,
  "R1": uinput.KEY_F11,
  "R2": uinput.BTN_MIDDLE,
}
AXIS_MAP = {
  0: uinput.REL_X,
  1: uinput.REL_Y,
  2: uinput.REL_X,
  3: uinput.REL_Y,
}
HAT_MAP = {
  "LEFT": uinput.KEY_LEFT,
  "RIGHT": uinput.KEY_RIGHT,
  "UP": uinput.KEY_UP,
  "DOWN": uinput.KEY_DOWN,
}

EVENTS = list(BUTTON_MAP.values()) + list(AXIS_MAP.values())
keydev = uinput.Device(EVENTS)
pygame.init()

# Set the width and height of the screen (width, height).
#screen = pygame.display.set_mode((500, 700))
#pygame.display.set_caption("My Game")

# Loop until the user clicks the close button.
done = False
# Used to manage how fast the screen updates.
clock = pygame.time.Clock()
# Initialize the joysticks.
pygame.joystick.init()

# Get count of joysticks.
joystick_count = pygame.joystick.get_count()
print("Number of joysticks: {}".format(joystick_count))

joystick = pygame.joystick.Joystick(JSDEV)
joystick.init()
print("Selected joystick device {}".format(JSDEV))

# Get the name from the OS for the controller/joystick.
name = joystick.get_name()
print("Joystick name: {}".format(name))

# Usually axis run in pairs, up/down for one, and left/right for
# the other.
axes = joystick.get_numaxes()
print("Number of axes: {}".format(axes))
buttons = joystick.get_numbuttons()
print("Number of buttons: {}".format(buttons))
hats = joystick.get_numhats()
print("Number of hats: {}".format(hats))

def on_button_down(ev):
  name = BUTTON_NAMES[ev.button]
  if name in BUTTON_MAP:
    keydev.emit(BUTTON_MAP[name], 1)

def on_button_up(ev):
  name = BUTTON_NAMES[ev.button]
  if name in BUTTON_MAP:
    keydev.emit(BUTTON_MAP[name], 0)

def on_axis_motion(ev):
  axis = ev.axis
  if axis in AXIS_MAP:
    delta = ev.value
    value = 0
    if delta < -0.5:
      value = -5
    elif delta > 0.5:
      value = 5
    keydev.emit(AXIS_MAP[axis], value)

tracker_hat = {}
def on_hat_motion(ev):
  keys = ['LEFT', 'RIGHT', 'UP', 'DOWN']
  values = {}
  for k in keys:
    if k not in tracker_hat:
      tracker_hat[k] = 0
    values[k] = 0
  x, y = ev.value
  if x <= -1:
    values['LEFT'] = 1
  elif x>= 1:
    values['RIGHT'] = 1
  if y <= -1:
    values['DOWN'] = 1
  elif y>= 1:
    values['UP'] = 1
  for k in keys:
    if not values[k] == tracker_hat[k]:
      if k in HAT_MAP:
        keydev.emit(HAT_MAP[k], values[k])
      tracker_hat[k] = values[k]

tracker_ax = {}
def update_axis_motion():
  global tracker_ax
  axises = AXIS_MAP.keys()
  for k in axises:
    if not k in tracker_ax:
      tracker_ax[k] = {'delta':0,'count':0}
    val = joystick.get_axis(k)
    if val > -0.5 and val < 0.5:
      tracker_ax[k] = {'delta':0,'count':0}
      continue
    delta = -1 if val <= -0.5 else 1
    if not delta == tracker_ax[k]['delta']: # First triggered
      tracker_ax[k] = {'delta':delta,'count':1}
    else:
      tracker_ax[k]['count'] += 1
    speed = min(tracker_ax[k]['count'], 20)
    keydev.emit(AXIS_MAP[k], delta*speed)

def update_hat_motion():
  (x, y) = joystick.get_hat(0)
  if not x == 0:
    delta = -1 if x < 0 else 1
    keydev.emit(uinput.REL_X, delta)
  if not y == 0:
    delta = -1 if y > 0 else 1
    keydev.emit(uinput.REL_Y, delta)

# -------- Main Program Loop -----------
delay = int(1.0/FPS)
while not done:
    #
    # EVENT PROCESSING STEP
    #
    # Possible joystick actions: JOYAXISMOTION, JOYBALLMOTION, JOYBUTTONDOWN,
    # JOYBUTTONUP, JOYHATMOTION
    for event in pygame.event.get(): # User did something.
      if event.type == pygame.QUIT: # If user clicked close.
        done = True # Flag that we are done so we exit this loop.
      elif event.type == pygame.JOYBUTTONDOWN:
        print("Joystick button down.", event)
        on_button_down(event)
      elif event.type == pygame.JOYBUTTONUP:
        print("Joystick button up.", event)
        on_button_up(event)
      elif event.type == pygame.JOYAXISMOTION:
        print("Joystick axis motion.", event)
        #on_axis_motion(event)
      elif event.type == pygame.JOYBALLMOTION:
        print("Joystick ball motion.", event)
      elif event.type == pygame.JOYHATMOTION:
        print("Joystick hat motion.", event)
        on_hat_motion(event)
    update_axis_motion()
    #update_hat_motion()

    """
    for i in range(axes):
      axis = joystick.get_axis(i)
      print("Axis {} value: {:>6.3f}".format(i, axis))
    for i in range(buttons):
      button = joystick.get_button(i)
      print("Button {:>2} value: {}".format(i, button))
    for i in range(hats):
      hat = joystick.get_hat(i)
      print("Hat {} value: {}".format(i, str(hat)))
    """
    # Limit to FPS frames per second.
    clock.tick(FPS)
    #time.sleep(delay)

# Close the window and quit.
# If you forget this line, the program will 'hang'
# on exit if running from IDLE.
pygame.quit()
