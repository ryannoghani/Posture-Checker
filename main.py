import cv2
import time
import numpy as np
import os
import threading
import tkinter as tk
from tkinter import messagebox
from skimage.metrics import structural_similarity as ssim
import warnings

warnings.filterwarnings("ignore")

# -------------------------
# Helper Functions
# -------------------------

def mean_squared_error(image1, image2):
    error = np.sum((image1.astype('float') - image2.astype('float'))**2)
    error /= float(image1.shape[0] * image2.shape[1])
    return error

def image_comparison(image1, image2):
    image2 = cv2.resize(image2, (image1.shape[1::-1]), interpolation=cv2.INTER_AREA)
    m = mean_squared_error(image1, image2)
    s = ssim(image1, image2, channel_axis=-1)
    print(f"MSE: {m:.2f}, SSIM: {s:.2f}")
    return s

def take_a_pic(pic_name):
    cam = cv2.VideoCapture(0)
    time.sleep(1)

    if not cam.isOpened():
        print("Error: Could not open webcam.")
        return None

    result, image = cam.read()

    cam.release()

    if result:
        cv2.imwrite(pic_name + ".png", image)
        return image
    else:
        print("Error: Could not read frame.")
        return None

# -------------------------
# Main Application
# -------------------------

class PostureApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Posture Checker")
        self.root.geometry("300x200")

        self.reference_image = None
        self.running = False

        self.label = tk.Label(root, text="Posture Checker", font=("Helvetica", 16))
        self.label.pack(pady=10)

        self.capture_button = tk.Button(root, text="Capture Good Posture", command=self.capture_posture)
        self.capture_button.pack(pady=10)

        self.start_button = tk.Button(root, text="Start Monitoring", command=self.start_monitoring, state="disabled")
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(root, text="Stop Monitoring", command=self.stop_monitoring, state="disabled")
        self.stop_button.pack(pady=10)

    def capture_posture(self):
        image = take_a_pic("good_posture")
        if image is not None:
            self.reference_image = image
            messagebox.showinfo("Success", "Good posture captured successfully!")
            self.start_button.config(state="normal")

    def start_monitoring(self):
        if self.reference_image is None:
            messagebox.showwarning("Warning", "Capture a good posture first!")
            return
        self.running = True
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        threading.Thread(target=self.monitor_posture, daemon=True).start()

    def stop_monitoring(self):
        self.running = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")

    def monitor_posture(self):
        while self.running:
            current_image = take_a_pic("current_posture")
            if current_image is not None:
                similarity = image_comparison(self.reference_image, current_image)
                if similarity < 0.87:
                    print("Bad posture detected!")
                    os.system('say "Fix your posture!"')
            time.sleep(2)  # Wait for 2 seconds before next check

# -------------------------
# Run the App
# -------------------------

if __name__ == "__main__":
    root = tk.Tk()
    app = PostureApp(root)
    root.mainloop()
