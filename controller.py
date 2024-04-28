import ctypes
import threading
import time

import win32con
import win32gui
import win32ui
from PIL import Image
from pynput.keyboard import Key
from load_config import (PRESS_AND_HOLD, RANGE_LIMIT, SHOT_DELAY,
                         TAP_AND_RELEASE)

# Define constants
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010

# Define SendInput structures
PUL = ctypes.POINTER(ctypes.c_ulong)

class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                ("mi", MouseInput),
                ("hi", HardwareInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]

class ActionThread(threading.Thread):
    def __init__(self, action, instance, enemy_distance, eppoint):
        super(ActionThread, self).__init__()
        self.action = action
        self.enemy_position = eppoint
        self.enemy_distance = enemy_distance
        self._keep_running = True
        self.ACTIONS = {
            0: instance.move_up,
            1: instance.move_down,
            2: instance.move_left,
            3: instance.move_right,
            4: instance.auto_aim,
            5: instance.manual_aim,
            6: instance.activate_gadget,
            7: instance.activate_super,
            8: instance.activate_hypercharge,
        }

    def stop(self):
        self._keep_running = False

    def run(self):
        while self._keep_running and self.action in range(3):
            self.execute_action()
        else:
            self.execute_action()

    def execute_action(self):
        action_func = self.ACTIONS.get(self.action, None)
        if action_func and (self.action != 5):
            action_func()
        elif action_func and self.action == 5 and self.enemy_position != None:
            action_func(self.enemy_distance, self.enemy_position)
            
class ControllerInstance:
    def __init__(self, window_name):
        self.window_name = window_name
        self.hwndMain = win32gui.FindWindow(None, window_name)
        self.hwndChild = win32gui.GetWindow(self.hwndMain, win32con.GW_CHILD)
    
    def screen_shot(self):
        # Get the dimensions of the window
        left, top, right, bot = win32gui.GetWindowRect(self.hwndChild)
        width = right - left
        height = bot - top
        # Create a device context for the window
        hwndDC = win32gui.GetWindowDC(self.hwndChild)
        mfcDC = win32ui.CreateDCFromHandle(hwndDC)
        saveDC = mfcDC.CreateCompatibleDC()

        # Create a bitmap and associate it with the compatible DC
        saveBitMap = win32ui.CreateBitmap()
        saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)

        saveDC.SelectObject(saveBitMap)

        # Copy the contents of the window to the bitmap
        result = saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)
        print(result)

        # Save the bitmap as an image file
        bmpinfo = saveBitMap.GetInfo()
        bmpstr = saveBitMap.GetBitmapBits(True)
        img = Image.frombuffer(
            'RGB',
            (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
            bmpstr, 'raw', 'BGRX', 0, 1)

        img.save(f'screen_{self.window_name}.png')

        # Clean up resources
        win32gui.DeleteObject(saveBitMap.GetHandle())
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(self.hwndChild, hwndDC)
        
        return img

    def send_keys_to_window(self, hwnd, keys):
        # Below we loop over the keys and handle what they are
        # Keys like up and down are seperated from the letters like ABCD
        for key in keys:
            if isinstance(key, str):
                vk_code = ord(key.upper())  # Get the virtual key code for the key
                time1, time2 = PRESS_AND_HOLD.values()
            else:
                vk_code = key.value.vk  # Get the virtual key code from the Key enum
                time1, time2 = TAP_AND_RELEASE.values()
            win32gui.PostMessage(hwnd, win32con.WM_KEYDOWN, vk_code, 0)
            time.sleep(time1)  # Add a small delay after each key press
            win32gui.PostMessage(hwnd, win32con.WM_KEYUP, vk_code, 0)
            time.sleep(time2)  # Add a small delay after each key release

    # Self-explanatory functions
    def press_game(self):
        self.send_keys_to_window(self.hwndChild, ['q'])
        time.sleep(8.5)

    def move_up(self):
        print(f'{self.window_name} - moving up')
        self.send_keys_to_window(self.hwndChild, [Key.up])

    def move_down(self):
        print(f'{self.window_name} - moving down')
        self.send_keys_to_window(self.hwndChild, [Key.down])

    def move_left(self):
        print(f'{self.window_name} - moving left')
        self.send_keys_to_window(self.hwndChild, [Key.left])

    def move_right(self):
        print(f'{self.window_name} - moving right')
        self.send_keys_to_window(self.hwndChild, [Key.right])

    def auto_aim(self):
        print(f'{self.window_name} - auto aiming')
        self.send_keys_to_window(self.hwndChild, ['e'])

    def activate_super(self):
        print(f'{self.window_name} - activating the super')
        self.send_keys_to_window(self.hwndChild, ['f'])

    def activate_gadget(self):
        print(f'{self.window_name} - activating the gadget')
        self.send_keys_to_window(self.hwndChild, ['q'])

    def activate_hypercharge(self):
        print(f'{self.window_name} - activating the hypercharge')
        self.send_keys_to_window(self.hwndChild, ['r'])
    
    def send_mouse_input(self, x, y, flags):
        mouse_input = MouseInput(dx=x, dy=y, mouseData=0, dwFlags=flags, time=0, dwExtraInfo=None)
        input_i = Input_I()
        input_i.mi = mouse_input
        input_obj = Input(type=ctypes.c_ulong(0), ii=input_i)
        ctypes.windll.user32.SendInput(1, ctypes.byref(input_obj), ctypes.sizeof(input_obj))
    
    def manual_aim(self, enemy_distance, eppoint):
        x, y = eppoint
        actual_screen_width, actual_screen_height = 1920, 1080
        img = Image.open(f'screen_{self.window_name}.png')
        screenshot_screen_width, screenshot_screen_height = img.size
        conversion_factor_x = actual_screen_width / screenshot_screen_width
        conversion_factor_y = actual_screen_height / screenshot_screen_height
        
        adjusted_x, adjusted_y = round(x * conversion_factor_x), round(y * conversion_factor_y)
        
        # Check if the enemy is within shooting range
        #if RANGE_LIMIT >= enemy_distance:
            #print(f'Enemy distance is: {enemy_distance} and is within shooting range')

        # Move the mouse cursor to the intersection point
        self.send_keys_to_window(self.hwndChild, ['p'])
        # Simulate aiming and shooting in the background
        self.send_mouse_input(adjusted_x, adjusted_y, MOUSEEVENTF_RIGHTDOWN)
        time.sleep(SHOT_DELAY)
        self.send_mouse_input(adjusted_x, adjusted_y, MOUSEEVENTF_RIGHTUP)
    
# Example usage
def start_action(action, instance, enemy_distance, eppoint):
    thread = ActionThread(action, instance, enemy_distance, eppoint)
    thread.start()
    return thread
