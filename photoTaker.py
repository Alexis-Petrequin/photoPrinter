import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import tkinter as tk
from tkinter import Button
from PIL import Image, ImageTk
import win32con as wcon
import win32ui as wui
from PIL import Image as pil_image, ImageWin as pil_image_win
import win32print

image_path = [""]
common_font = ('Helvetica', 16)

def list_printers():
    printer_info = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
    printers = []
    for printer in printer_info:
        if isinstance(printer, tuple):
            printer_name = printer[2]
            printers.append(printer_name)
    return printers

printers = list_printers()
for printer in printers:
    print(printer)

global printer_to_use
printer_to_use = input("Enter the name of the printer you want to use (use the names listed above): ")

def get_image_path():
    def set_image_path():
        image = entry_image_path.get()
        image_path[0] = image
        popup.destroy()
        root.destroy()
    root = tk.Tk()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    popup = tk.Toplevel()
    popup.title("Enter your folder path")
    popup_width = screen_width - 850
    popup_height = screen_height - 600
    x_position = (screen_width - popup_width) // 2
    y_position = (screen_height - popup_height) // 2
    popup.geometry(f"{popup_width}x{popup_height}+{x_position}+{y_position}")
    label_image_path = tk.Label(popup, text="Enter the path of the folder that will contain your images :", font=common_font)
    label_image_path.pack(pady=10)
    entry_image_path = tk.Entry(popup, font=common_font)
    entry_image_path.pack(pady=10, padx=10, fill=tk.X)
    button_set_image_path = Button(popup, text="OK", command=set_image_path, font=('Helvetica', 12))
    button_set_image_path.pack(pady=10)
    popup.mainloop()

get_image_path()

def choose_mode():
    def open_graphical_interface():
        global auto_print_flag
        auto_print_flag = False
        graphical_interface.destroy()

    def auto_print():
        global auto_print_flag
        auto_print_flag = True
        graphical_interface.destroy()
    graphical_interface = tk.Tk()
    graphical_interface.title("Choose Mode")
    screen_width = graphical_interface.winfo_screenwidth()
    screen_height = graphical_interface.winfo_screenheight()
    popup_width = screen_width - 850
    popup_height = screen_height - 600
    x_position = (screen_width - popup_width) // 2
    y_position = (screen_height - popup_height) // 2
    graphical_interface.geometry(f"{popup_width}x{popup_height}+{x_position}+{y_position}")
    label_mode = tk.Label(graphical_interface, text="Choose your mode :", font=common_font)
    label_mode.pack(pady=10)
    button_graphical_interface = Button(graphical_interface, text="Choose the photos you want to print", command=open_graphical_interface, font=('Helvetica', 12))
    button_graphical_interface.pack(pady=10)
    button_auto_print = Button(graphical_interface, text="Print every new photos in the folder", command=auto_print, font=('Helvetica', 12))
    button_auto_print.pack(pady=10)
    graphical_interface.mainloop()

choose_mode()

def draw_img(hdc, dib, maxh, maxw):
    w, h = dib.size
    h = min(h, maxh)
    w = min(w, maxw)
    l = (maxw - w) // 2
    t = (maxh - h) // 2
    dib.draw(hdc, (l, t, l + w, t + h))

def add_img(hdc, file_name, new_page=False):
    if new_page:
        hdc.StartPage()
    maxw = hdc.GetDeviceCaps(wcon.HORZRES)
    maxh = hdc.GetDeviceCaps(wcon.VERTRES)
    img = pil_image.open(file_name)
    dib = pil_image_win.Dib(img)
    draw_img(hdc.GetHandleOutput(), dib, maxh, maxw)
    if new_page:
        hdc.EndPage()

def printPhoto(image_path):
    printer_name = printer_to_use
    hdc = wui.CreateDC()
    hdc.CreatePrinterDC(printer_name)
    hdc.StartDoc(image_path)
    hdc.StartPage ()
    add_img(hdc, image_path)
    hdc.EndPage ()
    hdc.EndDoc()
    print("Image sent successfully")

def display_image(image_path):
    def validate_image():
        printPhoto(image_path)
        root.destroy()

    def cancel_image():
        root.destroy()

    root = tk.Tk()
    root.title("Photo")
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.attributes("-fullscreen", True)
    img = Image.open(image_path)
    img.thumbnail((screen_width - 210, screen_height - 230))
    img = ImageTk.PhotoImage(img)
    img_label = tk.Label(root, image=img)
    img_label.image = img
    img_label.pack(fill=tk.BOTH, expand=True)
    button_frame = tk.Frame(root)
    button_frame.pack(side=tk.BOTTOM, pady=10)
    Validate_button = Button(button_frame, text="Print", command=validate_image, font=common_font, padx=20, pady=10)
    Validate_button.pack(side=tk.LEFT, padx=10)
    cancel_button = Button(button_frame, text="Cancel", command=cancel_image, font=common_font, padx=20, pady=10)
    cancel_button.pack(side=tk.RIGHT, padx=10)
    root.mainloop()

class ImageHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            print(f"New image detected: {event.src_path}")
            if auto_print_flag:
                printPhoto(event.src_path)
            else:
                display_image(event.src_path)

if __name__ == "__main__":
    event_handler = ImageHandler()
    observer = Observer()
    observer.schedule(event_handler, path=image_path[0], recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()