# PyMobileDevice3-Simple-Gui

# iOS Control Tool

A modern desktop application to manage iOS devices, run commands, browse files, and view live logs — built with Python and [`pymobiledevice3`](https://github.com/Blackjacx/pymobiledevice3).  
Features a sleek dark interface powered by [`customtkinter`](https://github.com/TomSchimansky/CustomTkinter).

---

## 🚀 Features

### Device Management
- Auto-detect connected iOS devices
- Live UDID selection
- Device info panel (model, iOS version, name)
- Auto-refresh when devices are plugged/unplugged

### Command Runner
- Execute any `pymobiledevice3` command
- Supports arguments
- Output displayed in real-time

### File Manager
- Browse device filesystem (e.g., `/Books`)
- Upload and download files
- Delete files
- Navigate folders easily

### Logs
- Real-time device syslog
- Start / stop streaming
- Works with selected device

### Modern UI
- Dark theme with `customtkinter`
- Sidebar navigation for Commands, Files, and Logs
- Clean, user-friendly interface

---

## 💻 Requirements

- Python 3.10+
- [`pymobiledevice3`](https://github.com/Blackjacx/pymobiledevice3)
- [`customtkinter`](https://github.com/TomSchimansky/CustomTkinter)

Install dependencies:

```bash
pip install pymobiledevice3 customtkinter
