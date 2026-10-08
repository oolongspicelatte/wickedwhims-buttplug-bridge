# Installation Guide

This guide will walk you through setting up the WickedWhims ↔ Buttplug Toy Bridge from scratch, even if you have no programming experience.

## Prerequisites

Before starting, make sure you have:

1. **Windows PC** (this guide assumes Windows; the script itself is cross-platform, but the steps below focus on Windows)
2. **The Sims 4** with the **[WickedWhims mod](https://wickedwhimsmod.com/)** installed and working
3. A **Buttplug.io-compatible toy** with Bluetooth connectivity (see the [full list of supported devices](https://iostindex.com/))
4. A Bluetooth adapter on your PC (built-in or USB dongle)

---

## Step 1: Install Python

1. Go to [python.org/downloads](https://www.python.org/downloads/)
2. Download the latest version for Windows
3. Run the installer
4. ⚠️ **Important:** Check the box **"Add Python to PATH"** at the bottom of the installer window
5. Click **"Install Now"**

**Verify the installation:**
- Press `Win + R`, type `cmd`, press Enter
- Type: `python --version`
- You should see something like `Python 3.12.0`

---

## Step 2: Download this repository

**Option A — Download as ZIP (easiest for non-programmers):**

1. On this GitHub repository page, click the green **"Code"** button
2. Click **"Download ZIP"**
3. Extract the ZIP file to a folder, e.g. `C:\WW_Bridge`

**Option B — Clone with Git (if you have Git installed):**

```bash
git clone https://github.com/oolongspicelatte/wickedwhims-buttplug-bridge.git
```

---

## Step 3: Install dependencies

1. Open the folder where you extracted/cloned the repository
2. In the folder's address bar, type `cmd` and press Enter (this opens a command prompt in that folder)
3. Run:
   ```bash
   pip install -r requirements.txt
   ```
4. Wait for the installation to finish (you should see `Successfully installed buttplug-py...`)

---

## Step 4: Install and configure Intiface Central

Intiface Central is the app that handles the actual Bluetooth connection to your toy.

1. Download it from [intiface.com/central](https://intiface.com/central/)
2. Install and launch the app
3. Click the large **Play button** (top-left corner) to start the engine
   - The status will change to **"Engine running, waiting for client"**
   - The button icon will change from a play triangle to a stop square
   - The server address will be shown as `ws://0.0.0.0:12345` — this is the default and what the bridge script expects

**Connect your toy:**

1. Turn on your toy (usually a long button press) and put it in pairing mode
2. Make sure Bluetooth is enabled on your PC
3. Click **"Devices"** in the left sidebar
4. Click **"Start Scanning"**
5. Your toy should appear in the list (showing its name and a Bluetooth icon)
6. Click on the device entry to connect to it
7. ✅ Confirm the toy shows as connected before moving on

**Optional — fine-tune your device:**

Once connected, you can click on your device in the Devices tab to access additional settings, such as capping maximum/minimum intensity or disabling specific motors/features you don't want active. This is entirely optional and handled by Intiface Central itself, independently of the bridge script.

---

## Step 5: Configure WickedWhims in-game

1. Launch **The Sims 4** and enter Live Mode
2. Open the WickedWhims settings
3. Go to **Settings → Toy Settings**
4. Click **"Connect Device"**
5. A dialog box will appear asking for a local IP and port
6. Enter the following:
   - **First field (IP):** `127.0.0.1`
   - **Second field (Port):** `60069`
7. Click **"Connect"**

> **Note:** Menu wording may vary slightly depending on your WickedWhims version.

8. **Don't start a scene yet** — first you need to start the bridge script (next step)

---

## Step 6: Run the bridge

**Correct startup order matters!** Always start things in this sequence:

1. ✅ **Intiface Central** is running, engine started, toy connected
2. ▶️ **Run the bridge script**
3. 🎮 **Then** connect the Custom Device in WickedWhims

**To run the script:**

1. Open the repository folder
2. Open a command prompt there (type `cmd` in the address bar, press Enter)
3. Run:
   ```bash
   python bridge.py
   ```
4. You should see output similar to:
   ```
   =======================================================
      WickedWhims <-> Buttplug Toy Bridge
   =======================================================
   [timestamp] [INFO] Connecting to Intiface Central...
   [timestamp] [INFO] Connected to Intiface Central
   [timestamp] [INFO] Scanning for devices (4s)...
   [timestamp] [INFO] Selected device: <your toy's name>
   [timestamp] [INFO] Server for WickedWhims started: 127.0.0.1:60069
   ```

5. **Keep this window open** while playing — closing it will disconnect the bridge

Now go back to the game and click **"Connect"** in the WickedWhims Toy Settings menu.

---

## Step 7: Test it

1. Start any sex animation scene in-game via WickedWhims
2. Watch the bridge's console window — you should see log lines like:
   ```
   Action: vibrate | strength=75% | duration=500ms
   ```
3. Your toy should react accordingly

---

## Stopping the bridge

1. Disconnect the Custom Device in the WickedWhims in-game menu
2. In the bridge's console window, press `Ctrl + C`

---

## Troubleshooting

If something isn't working, check **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** for common issues and solutions.