
from pynput.keyboard import Key, Controller


keyboard = Controller()

# Below is the chaapu code to simulate key press using position of com
if cx > (width / 2) + 70 and center:
    center = False
    left = True
    print('Left')
    keyboard.press(Key.left)
    # keyboard.release(Key.left)
if cx > width / 2 - 70 and cx < width / 2 + 70 and not center:
    center = True
    if left:
        print('left released')
        keyboard.release(Key.left)
        left = False
    elif right:
        print('right released')
        keyboard.release(Key.right)
        right = False
if cx < width / 2 - 70 and center:
    center = False
    right = True
    print('Right')
    keyboard.press(Key.right)
    # keyboard.release(Key.right)