import threading
import time

import win32api
import win32con
import win32gui
import win32ui
from PIL import Image
from pynput.keyboard import Key

import load_config


class ActionThread(threading.Thread):
    def __init__(self, action, instance):
        super(ActionThread, self).__init__()
        self.action = action
        self._keep_running = True
        self.ACTIONS = {
            0: instance.move_up,
            1: instance.move_down,
            2: instance.move_left,
            3: instance.move_right,
            4: instance.auto_aim,
            5: instance.activate_gadget,
            6: instance.activate_super,
            7: instance.activate_hypercharge,
        }

    def stop(self):
        self._keep_running = False

    def run(self):
        while self._keep_running and self.action in range(0,4):
            self.execute_action()
        else:
            self.execute_action()

    def execute_action(self):
        action_func = self.ACTIONS.get(self.action, None)
        if action_func:
            action_func()
            
class LDPlayerInstance:
    def __init__(self, window_name):
        self.window_name = window_name
        hwndMain = win32gui.FindWindow(None, window_name)
        self.hwndChild = win32gui.GetWindow(hwndMain, win32con.GW_CHILD)
    
    def screen_shot(self, emulator_name):
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
        #result = saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)
        #print(result)

        # Save the bitmap as an image file
        bmpinfo = saveBitMap.GetInfo()
        bmpstr = saveBitMap.GetBitmapBits(True)
        img = Image.frombuffer(
            'RGB',
            (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
            bmpstr, 'raw', 'BGRX', 0, 1)

        img.save(f'screen_{emulator_name}.png')

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
                time1, time2 = load_config.PRESS_AND_HOLD.values()
            else:
                vk_code = key.value.vk  # Get the virtual key code from the Key enum
                time1, time2 = load_config.TAP_AND_RELEASE.values()
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
        
    def manual_aim(x, y):
        # This function is current in beta and might not work as intended...
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, x, y, 0, 0)
        time.sleep(0.5)  # You may adjust the delay as needed
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, x, y, 0, 0)
        
# Example usage
def start_action(action, instance):
    thread = ActionThread(action, instance)
    thread.start()
    return thread
