# Troubleshooting

This page covers common issues you might encounter and how to resolve them.

---

## Intiface Central can't find my toy

**Possible solutions:**

1. Make sure your toy is **fully charged** and powered on
2. Put the toy into **pairing mode** (usually a long button press — check your toy's manual)
3. Make sure **Bluetooth is enabled** on your PC
4. Make sure the Intiface Central **engine is running** (the Play button) *before* scanning — see [INSTALLATION.md](INSTALLATION.md) Step 4
5. In Intiface Central, go to **Devices → Start Scanning**
6. If the toy still doesn't appear, try removing it from Windows' Bluetooth settings and re-pairing from scratch

---

## "ModuleNotFoundError: No module named 'buttplug'"

**Cause:** The `buttplug-py` package isn't installed.

**Solution:**
```bash
pip install -r requirements.txt
```

If that doesn't work, try installing the package directly:
```bash
pip install buttplug-py
```

---

## "Address already in use" error when starting the bridge

**Cause:** Another instance of the bridge script is already running and using the same port.

**Solution:**
1. Close any previously running instance of `bridge.py`
2. If the problem persists, restart your PC to free up the port
3. Alternatively, change `WICKEDWHIMS_PORT` in the script to a different number (and match it in WickedWhims' in-game settings)

---

## Nothing happens when I start a scene in-game

**Possible causes & solutions:**

1. **Startup order matters.** Make sure you started things in this exact sequence: Intiface Central (engine running, toy connected) → `bridge.py` → Connect Device in WickedWhims. See [INSTALLATION.md](INSTALLATION.md) for the full sequence.
2. **Check the bridge console.** If you don't see any `Action: ...` log lines appearing when a scene starts, the connection between the game and the bridge likely isn't established — double-check the IP/port entered in-game matches the script's settings (default: `127.0.0.1` / `60069`).
3. **Check Intiface Central.** Make sure your toy still shows as connected there — Bluetooth connections can sometimes drop silently.

---

## How does the toy know when to stop?

The bridge automatically stops the toy once there are no more pending actions in the queue. This happens automatically based on the `duration` values sent by WickedWhims for each action — you don't need to manually stop it after a scene ends.

---

## Still having issues?

If none of the above solved your problem, please open an [Issue on GitHub](../../issues) with:

1. The full console output from `bridge.py`
2. What you expected to happen vs. what actually happened
3. Your toy's brand/model
4. Your Intiface Central version (visible in the app's title bar)