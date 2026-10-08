"""
WickedWhims <-> Buttplug.io Toy Bridge
A bridge between the WickedWhims mod (The Sims 4) and any
Buttplug.io-compatible toy via Intiface Central.
"""

from __future__ import annotations

import asyncio
import json
import logging
import traceback
from typing import Any

from buttplug import Client, WebsocketConnector, ProtocolSpec

# ================= SETTINGS =================
WICKEDWHIMS_HOST = '127.0.0.1'
WICKEDWHIMS_PORT = 60069
INTIFACE_WS_URL = 'ws://127.0.0.1:12345'
PREFERRED_DEVICE_NAME: str | None = None
SCAN_DURATION = 4

# How often to check if the current action is outdated (in seconds).
# Lower value = faster reaction to animation changes, but slightly more CPU load.
INTERRUPT_CHECK_INTERVAL = 0.05

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
log = logging.getLogger("Bridge")


class ToyBridge:
    """Manages the connection to Intiface Central and executes toy actions.

    Incoming actions are processed through a queue tagged with a
    "generation" number. Each new batch of actions from the game increments
    this counter, which lets already-queued or in-progress actions detect
    that they're outdated and stop early — without needing to cancel
    asyncio tasks directly. This keeps the execution loop simple and avoids
    having to handle CancelledError around toy I/O calls.
    """

    def __init__(self) -> None:
        self.bp_client: Client | None = None
        self.device: Any = None
        self.action_queue: asyncio.Queue[tuple[int, dict[str, Any]]] = asyncio.Queue()
        self._worker_task: asyncio.Task[None] | None = None
        self.current_generation: int = 0

    async def connect_buttplug(self) -> bool:
        """Connect to Intiface Central and select a target device.

        Returns:
            True if a device was found and selected, False otherwise.
        """
        self.bp_client = Client("WickedWhims Bridge", ProtocolSpec.v3)
        connector = WebsocketConnector(INTIFACE_WS_URL, logger=self.bp_client.logger)
        await self.bp_client.connect(connector)
        log.info("Connected to Intiface Central")

        await self.bp_client.start_scanning()
        log.info(f"Scanning for devices ({SCAN_DURATION}s)...")
        await asyncio.sleep(SCAN_DURATION)
        await self.bp_client.stop_scanning()

        if not self.bp_client.devices:
            return False

        devices = list(self.bp_client.devices.values())

        if PREFERRED_DEVICE_NAME:
            for d in devices:
                if PREFERRED_DEVICE_NAME.lower() in d.name.lower():
                    self.device = d
                    break

        if self.device is None:
            self.device = devices[0]

        log.info(f"Selected device: {self.device.name}")
        return True

    def start_worker(self) -> None:
        """Start the background task that processes queued actions."""
        self._worker_task = asyncio.create_task(self._process_queue())

    async def _process_queue(self) -> None:
        """Continuously consume and execute actions from the queue."""
        while True:
            generation, action = await self.action_queue.get()

            # If this action belongs to an outdated generation, skip it
            # without execution (e.g. it's leftover from a pattern that
            # has already been interrupted by a newer one).
            if generation != self.current_generation:
                self.action_queue.task_done()
                continue

            try:
                await self._execute_action(action, generation)
            except Exception as e:
                log.error(f"Error executing action {action}: {e}")
            finally:
                self.action_queue.task_done()
                if self.action_queue.empty() and generation == self.current_generation:
                    await self._stop_device()

    async def enqueue_actions(self, actions: list[dict[str, Any]]) -> None:
        """Replace the current action queue with a new batch.

        A new batch completely REPLACES the old one instead of being
        appended to the end. This eliminates the delay that would
        otherwise occur when switching animations/categories in-game.
        """
        self.current_generation += 1
        my_generation = self.current_generation

        await self.clear_queue()

        for action in actions:
            await self.action_queue.put((my_generation, action))

    async def clear_queue(self) -> None:
        """Remove all pending actions from the queue."""
        while not self.action_queue.empty():
            try:
                self.action_queue.get_nowait()
                self.action_queue.task_done()
            except asyncio.QueueEmpty:
                break

    async def _execute_action(self, action: dict[str, Any], generation: int) -> None:
        """Execute a single action, interruptibly waiting out its duration."""
        action_type = action.get('action')
        strength = action.get('strength', 0)
        duration = action.get('duration', 0)
        log.info(f"Action: {action_type} | strength={strength}% | duration={duration}ms")

        if action_type == 'stop':
            self.current_generation += 1  # invalidate anything left in queue
            await self.clear_queue()
            await self._stop_device()
            return
        else:
            await self._set_vibration(strength)

        # Interruptible wait: instead of a single sleep() for the whole
        # duration, sleep in small chunks and repeatedly check whether
        # this action has become outdated (i.e. a new pattern has arrived).
        remaining = duration / 1000.0
        while remaining > 0:
            if generation != self.current_generation:
                # A new pattern has arrived — stop waiting immediately
                return
            sleep_time = min(INTERRUPT_CHECK_INTERVAL, remaining)
            await asyncio.sleep(sleep_time)
            remaining -= sleep_time

    async def _set_vibration(self, strength_percent: int) -> None:
        """Send an intensity value to all of the device's actuators."""
        if self.device is None:
            return
        intensity = max(0.0, min(1.0, strength_percent / 100.0))
        try:
            for actuator in self.device.actuators:
                await actuator.command(intensity)
        except Exception as e:
            log.error(f"Error setting vibration: {e}")

    async def _stop_device(self) -> None:
        """Stop all actuators on the device."""
        if self.device is None:
            return
        try:
            await self.device.stop()
        except Exception as e:
            log.error(f"Error stopping device: {e}")

    async def disconnect(self) -> None:
        """Clean up the queue, worker task, and Buttplug connection."""
        self.current_generation += 1
        await self.clear_queue()
        if self._worker_task:
            self._worker_task.cancel()
        await self._stop_device()
        if self.bp_client:
            await self.bp_client.disconnect()


class WickedWhimsListener:
    """Implements WickedWhims' Custom Device Listener TCP protocol."""

    def __init__(self, bridge: ToyBridge) -> None:
        self.bridge = bridge

    async def handle_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        """Handle a single incoming connection from WickedWhims."""
        addr = writer.get_extra_info('peername')
        log.info(f"WickedWhims connected: {addr}")
        try:
            while True:
                header = await reader.readexactly(10)
                msg_size = int(header.decode('utf-8').strip())
                data = await reader.readexactly(msg_size)
                message = json.loads(data.decode('utf-8'))
                await self.process_message(message, writer)

        except asyncio.IncompleteReadError:
            log.info(f"WickedWhims disconnected (normal closure): {addr}")
        except Exception as e:
            log.error(f"ERROR while handling connection {addr}: {e}")
            log.error(traceback.format_exc())
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass

    async def process_message(
        self, message: dict[str, Any], writer: asyncio.StreamWriter
    ) -> None:
        """Dispatch an incoming message to the appropriate handler."""
        command = message.get('command')

        if command == 'GetDevices':
            device_name = self.bridge.device.name if self.bridge.device else "Unknown Device"
            device_model = getattr(self.bridge.device, 'display_name', None) or 'Generic Toy'

            response = {
                'devices': [{
                    'device_name': device_name,
                    'device_model': device_model,
                }]
            }
            await self._send_response(writer, response)
            log.info("Sent device info (handshake)")

        elif command == 'Actions':
            actions = message.get('actions', [])
            await self.bridge.enqueue_actions(actions)

        else:
            log.warning(f"Unknown command: {command}")

    async def _send_response(
        self, writer: asyncio.StreamWriter, response: dict[str, Any]
    ) -> None:
        """Send a plain JSON response (no length header, per WickedWhims' protocol)."""
        data = json.dumps(response).encode('utf-8')
        writer.write(data)
        await writer.drain()


async def main() -> None:
    print("=" * 55)
    print("   WickedWhims <-> Buttplug.io Toy Bridge")
    print("=" * 55)

    bridge = ToyBridge()

    log.info("Connecting to Intiface Central...")
    try:
        connected = await bridge.connect_buttplug()
    except Exception as e:
        log.error(f"Failed to connect to Intiface Central: {e}")
        log.error("Make sure the app is running and the WebSocket server is enabled")
        return

    if not connected:
        log.error("No device found. Please check:")
        log.error("  1. Bluetooth is enabled")
        log.error("  2. The toy is in pairing mode")
        log.error("  3. The device shows up in Intiface Central's device list")
        return

    bridge.start_worker()

    listener = WickedWhimsListener(bridge)
    server = await asyncio.start_server(listener.handle_client, WICKEDWHIMS_HOST, WICKEDWHIMS_PORT)

    log.info(f"Server for WickedWhims started: {WICKEDWHIMS_HOST}:{WICKEDWHIMS_PORT}")
    log.info("In-game: WickedWhims Settings -> Toy Settings -> Connect Device")
    log.info(f"  Host: {WICKEDWHIMS_HOST}")
    log.info(f"  Port: {WICKEDWHIMS_PORT}")

    try:
        async with server:
            await server.serve_forever()
    finally:
        await bridge.disconnect()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopping bridge...")