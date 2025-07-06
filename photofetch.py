import os
import time
import subprocess
import threading
from pynput import mouse, keyboard
from pynput.mouse import Controller as MouseController, Button
from pynput.mouse import Listener as MouseListener
from pynput.keyboard import Listener as KeyboardListener

# CSV & ADB Config
local_save_dir = "/Users/doganalisan/Projects/Python/marazmetal/photos/"
device_photo_dir = "/sdcard/DCIM/Camera/"
csv_path = "/Users/doganalisan/Projects/Python/marazmetal/product.csv"
check_interval = 5  # seconds

# Globals
photos_batch = []
mouse_lock_event = threading.Event()
mouse_lock_event.set()  # Mouse locking is active initially
latest_photo = None

# 📸 Get latest photo from device
def get_latest_device_photo():
    result = subprocess.run(
        ["adb", "shell", f"ls -t {device_photo_dir} | head -n 1"],
        capture_output=True, text=True
    )
    return result.stdout.strip()

# 📥 Pull a photo by filename
def pull_photo(filename):
    global full_local_path
    full_remote_path = device_photo_dir + filename
    full_local_path = os.path.join(local_save_dir, filename)
    subprocess.run(["adb", "pull", full_remote_path, full_local_path])
    print(f"✅ Pulled: {filename}")

# 🔄 Thread: Monitor device and pull new photos
def photo_monitor():
    print("🔍 Monitoring for new photos...")
    global latest_photo
    last_photo = None

    while True:
        try:
            latest_photo = get_latest_device_photo()
            if latest_photo and latest_photo != last_photo:
                pull_photo(latest_photo)
                last_photo = latest_photo
            time.sleep(check_interval)
        except Exception as e:
            print(f"⚠️ Error: {e}")
            time.sleep(5)

# 🖱️ Constantly lock mouse to (240, 570)
def move_mouse_to(x, y):
    mouse_ctrl = MouseController()
    while True:
        mouse_lock_event.wait()  # Pause if event is cleared
        mouse_ctrl.position = (x, y)
        time.sleep(0.1)

# 🖱️ On left-click: add latest photo to batch
def on_click(x, y, button, pressed):
    if pressed and button == Button.left:
        if latest_photo:
            photos_batch.append(latest_photo)
            print(f":p — Added photo: {latest_photo}")
        else:
            print(":p — No photo yet to add.")

# 🧾 Append a new row to the CSV
def update_product_csv(csv_path, new_data):
    if not os.path.exists(csv_path):
        print(f"❌ CSV file not found: {csv_path}")
        return

    with open(csv_path, "a+", encoding="utf-8") as f:
        f.write(new_data + "\n")
    print("✅ New product appended to CSV.")

# ⌨️ On key press
def on_key_press(key):
    try:
        # Pressed ":"
        if key.char == ':':
            print("⌨️ : key pressed — entering product info.")
            title = input("Title: ")
            short_description = input("Short Description: ")
            description = input("Description: ")
            price = input("Price: ")
            images = ''.join(x + "," for x in photos_batch)

            # WooCommerce CSV format line (adjust as needed)
            csv_line = f"Simple;;{title};1;1;visible;{short_description};{description};Taxable;1;15;{price};Uncategorized;{images}"
            update_product_csv(csv_path, csv_line)
            photos_batch.clear()
            print("🧹 Photos batch cleared.")

        # Pressed ";"
        elif key.char == ';':
            print("⌨️ ; key pressed — pausing mouse lock and clicking sequence.")
            mouse_lock_event.clear()  # ⏸ Pause mouse lock
            time.sleep(0.2)

            mouse_ctrl = MouseController()
            mouse_ctrl.position = (240, 610)
            mouse_ctrl.click(Button.left)
            time.sleep(3)

            mouse_ctrl.position = (250, 475)
            mouse_ctrl.click(Button.left)
            time.sleep(3)

            mouse_ctrl.position = (210, 530)
            mouse_ctrl.click(Button.left)
            time.sleep(3)

            mouse_lock_event.set()  # ▶️ Resume mouse lock
            print("🔁 Mouse lock resumed.")

    except AttributeError:
        pass  # Handles special keys like Ctrl, Shift

# 🧵 Start mouse + keyboard listeners
def start_listeners():
    mouse_listener = MouseListener(on_click=on_click)
    keyboard_listener = KeyboardListener(on_press=on_key_press)
    mouse_listener.start()
    keyboard_listener.start()
    mouse_listener.join()
    keyboard_listener.join()

# 🏁 Main
if __name__ == "__main__":
    os.makedirs(local_save_dir, exist_ok=True)

    threading.Thread(target=move_mouse_to, args=(240, 570), daemon=True).start()
    threading.Thread(target=start_listeners, daemon=True).start()
    threading.Thread(target=photo_monitor, daemon=True).start()

    while True:
        time.sleep(1)  # Keep main thread alive