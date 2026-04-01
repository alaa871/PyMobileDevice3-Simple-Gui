import customtkinter as ctk
import subprocess
import threading
import time
from tkinter import filedialog

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ===================== GLOBALS =====================
current_path = "/"
selected_udid = ""
log_process = None

# ===================== CORE =====================

def run_cmd(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, text=True)
    except subprocess.CalledProcessError as e:
        return e.output

def run_with_udid(cmd):
    if selected_udid:
        return run_cmd(f"pymobiledevice3 --udid {selected_udid} {cmd}")
    return run_cmd(f"pymobiledevice3 {cmd}")

# ===================== DEVICE =====================

def load_devices():
    output = run_cmd("pymobiledevice3 devices")
    return [line.split()[0] for line in output.splitlines() if line.strip()]

def set_device(choice):
    global selected_udid
    selected_udid = choice
    update_device_info()

def update_device_info():
    if not selected_udid:
        return

    output = run_with_udid("deviceinfo")

    info_box.configure(state="normal")
    info_box.delete("1.0", "end")

    for line in output.splitlines():
        if any(k in line.lower() for k in ["product", "version", "name"]):
            info_box.insert("end", line + "\n")

    info_box.configure(state="disabled")

def auto_refresh():
    prev = []
    while True:
        try:
            devices = load_devices()
            if devices != prev:
                device_menu.configure(values=devices)
                if devices:
                    device_menu.set(devices[0])
                    set_device(devices[0])
                prev = devices
        except:
            pass
        time.sleep(3)

# ===================== COMMAND =====================

def run_command():
    cmd = f"{cmd_entry.get()} {args_entry.get()}"
    output_box.delete("1.0", "end")
    output_box.insert("end", run_with_udid(cmd))

# ===================== FILE MANAGER =====================

def list_files(path):
    global current_path
    current_path = path

    output = run_with_udid(f"afc ls {path}")
    file_box.delete("0.0", "end")

    for line in output.splitlines():
        file_box.insert("end", line + "\n")

    path_label.configure(text=f"📂 {path}")

def enter_path(event=None):
    try:
        line = file_box.get("insert linestart", "insert lineend").strip()
        new_path = f"{current_path}/{line}".replace("//", "/")
        list_files(new_path)
    except:
        pass

def go_back():
    global current_path
    parent = "/".join(current_path.rstrip("/").split("/")[:-1])
    if not parent:
        parent = "/"
    list_files(parent)

def delete_file():
    try:
        line = file_box.get("insert linestart", "insert lineend").strip()
        run_with_udid(f"afc rm '{current_path}/{line}'")
        list_files(current_path)
    except:
        pass

def upload():
    f = filedialog.askopenfilename()
    if f:
        run_with_udid(f"afc push '{f}' '{current_path}/'")
        list_files(current_path)

def download():
    try:
        line = file_box.get("insert linestart", "insert lineend").strip()
        folder = filedialog.askdirectory()
        if folder:
            run_with_udid(f"afc pull '{current_path}/{line}' '{folder}'")
    except:
        pass

# ===================== LOGS =====================

def start_logs():
    global log_process
    stop_logs()

    cmd = "pymobiledevice3 syslog live"
    if selected_udid:
        cmd = f"pymobiledevice3 --udid {selected_udid} syslog live"

    log_process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, text=True)

    def stream():
        for line in log_process.stdout:
            log_box.insert("end", line)
            log_box.see("end")

    threading.Thread(target=stream, daemon=True).start()

def stop_logs():
    global log_process
    if log_process:
        log_process.terminate()
        log_process = None

# ===================== UI =====================

app = ctk.CTk()
app.geometry("1100x650")
app.title("iOS Control Tool")

# Sidebar
sidebar = ctk.CTkFrame(app, width=200)
sidebar.pack(side="left", fill="y")

main = ctk.CTkFrame(app)
main.pack(side="right", fill="both", expand=True)

# Device selector
device_menu = ctk.CTkOptionMenu(sidebar, values=[], command=set_device)
device_menu.pack(pady=10, padx=10)

info_box = ctk.CTkTextbox(sidebar, height=150)
info_box.pack(padx=10, pady=10)

# Views
frames = {}

def show(name):
    for f in frames.values():
        f.pack_forget()
    frames[name].pack(fill="both", expand=True)

# Buttons
ctk.CTkButton(sidebar, text="⚙ Commands", command=lambda: show("cmd")).pack(fill="x", padx=10, pady=5)
ctk.CTkButton(sidebar, text="📂 Files", command=lambda: show("files")).pack(fill="x", padx=10, pady=5)
ctk.CTkButton(sidebar, text="📟 Logs", command=lambda: show("logs")).pack(fill="x", padx=10, pady=5)

# COMMAND FRAME
frames["cmd"] = ctk.CTkFrame(main)

cmd_entry = ctk.CTkEntry(frames["cmd"], placeholder_text="Command (e.g. deviceinfo)")
cmd_entry.pack(pady=5)

args_entry = ctk.CTkEntry(frames["cmd"], placeholder_text="Arguments")
args_entry.pack(pady=5)

ctk.CTkButton(frames["cmd"], text="Run", command=run_command).pack(pady=5)

output_box = ctk.CTkTextbox(frames["cmd"])
output_box.pack(fill="both", expand=True, padx=10, pady=10)

# FILE FRAME
frames["files"] = ctk.CTkFrame(main)

path_label = ctk.CTkLabel(frames["files"], text="📂 /")
path_label.pack()

file_box = ctk.CTkTextbox(frames["files"])
file_box.pack(fill="both", expand=True)
file_box.bind("<Double-Button-1>", enter_path)

btns = ctk.CTkFrame(frames["files"])
btns.pack()

ctk.CTkButton(btns, text="⬅ Back", command=go_back).grid(row=0, column=0, padx=5)
ctk.CTkButton(btns, text="🗑 Delete", command=delete_file).grid(row=0, column=1, padx=5)
ctk.CTkButton(btns, text="⬆ Upload", command=upload).grid(row=0, column=2, padx=5)
ctk.CTkButton(btns, text="⬇ Download", command=download).grid(row=0, column=3, padx=5)

# LOG FRAME
frames["logs"] = ctk.CTkFrame(main)

ctk.CTkButton(frames["logs"], text="Start Logs", command=start_logs).pack(pady=5)
ctk.CTkButton(frames["logs"], text="Stop Logs", command=stop_logs).pack(pady=5)

log_box = ctk.CTkTextbox(frames["logs"])
log_box.pack(fill="both", expand=True)

# INIT
show("cmd")
list_files("/")

threading.Thread(target=auto_refresh, daemon=True).start()

app.mainloop()
