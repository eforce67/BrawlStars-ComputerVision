import threading
import time

import win32api
import win32con
import win32gui
import win32ui
from PIL import Image
from pynput.keyboard import Key


class ActionThread(threading.Thread):
    def __init__(self, action):
        super(ActionThread, self).__init__()
        self.action = action
        self._keep_running = True

    def stop(self):
        self._keep_running = False

    def run(self):
        while self._keep_running and self.action in [0, 1, 2, 3, 4]:
            self.execute_action()
        else:
            self.execute_action()

    def execute_action(self):
        ACTIONS = {
            0: move_up,
            1: move_down,
            2: move_left,
            3: move_right,
            4: stand_still,
            5: auto_aim,
            6: activate_gadget,
            7: activate_super,
            8: activate_hypercharge,
        }
        action_func = ACTIONS.get(self.action, None)
        if action_func:
            action_func()

# Example usage
def start_action(action):
    thread = ActionThread(action)
    thread.start()
    return thread

# Find the handle of the window
hwndMain = win32gui.FindWindow(None, "LDPlayer")
# Get the handle of the child window
hwndChild = win32gui.GetWindow(hwndMain, win32con.GW_CHILD)

def screen_shot():
    # Get the dimensions of the window
    left, top, right, bot = win32gui.GetWindowRect(hwndChild)
    width = right - left
    height = bot - top
    # Create a device context for the window
    hwndDC = win32gui.GetWindowDC(hwndChild)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()

    # Create a bitmap and associate it with the compatible DC
    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)

    saveDC.SelectObject(saveBitMap)

    # Copy the contents of the window to the bitmap
    result = saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)

    # Save the bitmap as an image file
    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)
    img = Image.frombuffer(
        'RGB',
        (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
        bmpstr, 'raw', 'BGRX', 0, 1)

    img.save('LDPlayer_screen.png')

    # Clean up resources
    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwndChild, hwndDC)
    
    return img

def send_keys_to_window(hwnd, keys):
    # Below we loop over the keys and handle what they are
    # Keys like up and down are separated from the letters like ABCD
    for key in keys:
        if isinstance(key, str):
            vk_code = ord(key.upper())  # Get the virtual key code for the key
        else:
            vk_code = key.value.vk  # Get the virtual key code from the Key enum
        win32gui.PostMessage(hwnd, win32con.WM_KEYDOWN, vk_code, 0)
        time.sleep(0.45)  # Add a small delay after each key press
        win32gui.PostMessage(hwnd, win32con.WM_KEYUP, vk_code, 0)
        time.sleep(0.05)  # Add a small delay after each key release

# Self-explanatory functions
def start_game():
    # the start button happens to be where the gadget button is
    send_keys_to_window(hwndChild, ['q'])
    time.sleep(10)

def exit_screen():
    for _ in range(2):
        send_keys_to_window(hwndChild, ['q'])
        time.sleep(2)
    
def stand_still():
    print('standing still')
    pass

def move_up():
    print('moving up')
    send_keys_to_window(hwndChild, [Key.up])

def move_down():
    print('moving down')
    send_keys_to_window(hwndChild, [Key.down])

def move_left():
    print('moving left')
    send_keys_to_window(hwndChild, [Key.left])

def move_right():
    print('moving right')
    send_keys_to_window(hwndChild, [Key.right])

def auto_aim():
    print('auto aiming')
    send_keys_to_window(hwndChild, ['e'])

def activate_super():
    print('activating the super')
    send_keys_to_window(hwndChild, ['f'])

def activate_gadget():
    print('activating the gadget')
    send_keys_to_window(hwndChild, ['q'])

def activate_hypercharge():
    print('activating the hypercharge')
    send_keys_to_window(hwndChild, ['r'])

def disable_afk():
    send_keys_to_window(hwndChild, [Key.up])
    send_keys_to_window(hwndChild, [Key.down])
    send_keys_to_window(hwndChild, [Key.left])
    send_keys_to_window(hwndChild, [Key.right])
    
def manual_aim(x, y):
    # This function is current in beta and might not work as intended...
    win32api.SetCursorPos((x, y))
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, x, y, 0, 0)
    time.sleep(0.5)  # You may adjust the delay as needed
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, x, y, 0, 0)
