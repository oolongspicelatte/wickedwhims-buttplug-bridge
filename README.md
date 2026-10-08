# WickedWhims ↔ Buttplug.io Toy Bridge

> ⚠️ **Status: Alpha**
> Built by a programming beginner with help from Claude (Anthropic AI). Tested on Satisfyer devices via Intiface Central. Other Buttplug.io-compatible toys/brands should work in theory but remain untested. See Known Limitations below before use.

A lightweight Python bridge that connects **[WickedWhims](https://wickedwhimsmod.com/)** (an adult mod for The Sims 4) to **any Buttplug.io-compatible toy**, using **[Intiface Central](https://intiface.com/central/)** as the Bluetooth communication layer.

In short: in-game sex animations in WickedWhims trigger real-time feedback on a connected toy.

This isn't limited to vibrators in theory — Buttplug.io supports various device types — though only vibration output has been tested so far. See [Known Limitations](#known-limitations) for details on how different in-game actions are currently handled.

---

## 🔞 Disclaimer

This is an 18+ project that requires the third-party adult mod **WickedWhims** for The Sims 4.

This project is **not affiliated with or endorsed by** Electronic Arts, TURBODRIVER (creator of WickedWhims), Satisfyer, or any other toy manufacturer. It simply acts as a translator between two existing, independent pieces of software.

---

## How it works

```
The Sims 4 (WickedWhims)  →  TCP socket  →  bridge.py  →  WebSocket  →  Intiface Central  →  Bluetooth  →  Your toy
```

1. WickedWhims has a built-in **Custom Device Listener** feature that sends vibration intensity/pattern data over a local TCP socket
2. This bridge script listens for that data, translates it into commands understood by the **Buttplug.io** protocol
3. Those commands are sent to **Intiface Central**, which handles the actual Bluetooth communication with your toy

---

## Features

- ✅ Real-time response to in-game sex animations
- ✅ Simple, single-file Python script — no complex setup beyond installing dependencies

---

## Requirements

- Windows PC (script is cross-platform in theory, but these docs focus on Windows)
- Python 3.10+
- The Sims 4 with WickedWhims mod installed
- Intiface Central
- A Buttplug.io-compatible Bluetooth toy ([supported device list](https://iostindex.com/))

---

## Quick Start

1. Install [Python](https://www.python.org/downloads/) (check "Add to PATH" during install)
2. Download this repository ([ZIP](../../archive/refs/heads/main.zip) or `git clone`)
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start [Intiface Central](https://intiface.com/central/), run the engine, and connect your toy
5. Run the bridge:
   ```bash
   python bridge.py
   ```
6. In WickedWhims: **Settings → Toy Settings → Connect Device** → enter `127.0.0.1` and `60069`

📖 **For detailed, step-by-step instructions (recommended for first-time setup), see [docs/INSTALLATION.md](docs/INSTALLATION.md)**

🔧 **Having issues? Check [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)**

---

## Configuration

All settings are located at the top of `bridge.py`:

```python
WICKEDWHIMS_HOST = '127.0.0.1'
WICKEDWHIMS_PORT = 60069
INTIFACE_WS_URL = 'ws://127.0.0.1:12345'
PREFERRED_DEVICE_NAME = None   # Set to a string to force a specific device
SCAN_DURATION = 4              # Seconds to scan for devices on startup
INTERRUPT_CHECK_INTERVAL = 0.05  # Lower = faster reaction to animation changes
```

### Per-device fine-tuning via Intiface Central

Independently of this bridge, **Intiface Central provides additional configuration options** for connected devices, such as:
- Setting a **maximum intensity limit**
- Setting a **minimum intensity threshold**
- **Disabling individual motors or features** on multi-function devices

These options are typically accessible by selecting the connected device within Intiface Central's **Devices** tab, allowing for configuration without modifying the bridge script.

---

## Known Limitations

- **No per-motor control.** On multi-motor devices (tested on Satisfyer models), the same intensity is sent to all motors simultaneously.
- **No action-type differentiation.** WickedWhims sends several action types (vibrate, pump, thrust, rotate, etc.) with different intended meanings, but this bridge currently treats all of them as a single generic intensity value — this is a limitation of the current implementation, not of the toy or the underlying protocol.
- **No GUI.** Configuration requires editing the Python script directly.
- **No automatic reconnection.** If Intiface Central or the toy disconnects mid-session, the script needs to be restarted.

---

## Contributing

This is an early-stage hobby project. If you test this with a different toy, encounter bugs, or have improvement ideas, feel free to open an [Issue](../../issues) or submit a Pull Request.

---

## Acknowledgments

- **TURBODRIVER** — creator of WickedWhims, whose [official Custom Device Listener documentation](https://turbodriver.itch.io/wickedwhims/devlog/892852/creating-wickedwhims-custom-sex-device-listener) made this bridge possible
- **[Buttplug.io](https://buttplug.io/)** — the open-source protocol and ecosystem that powers the toy control side of this project
- Built with the assistance of **Claude (Anthropic AI)**, based on the official WickedWhims Custom Device Listener documentation

---

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.