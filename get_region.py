import pyautogui
import mouse
import time

print("Nhấn chuột phải để in vị trí, nhấn Ctrl+C để thoát.")

try:
    while True:
        if mouse.is_pressed('left'):
            pos = pyautogui.position()
            print(f"👉 Vị trí chuột: {pos}")
            time.sleep(0.3)
except KeyboardInterrupt:
    print("\n🛑 Thoát chương trình")
