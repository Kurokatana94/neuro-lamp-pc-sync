from managers.rgb_sync_manager import SyncManager
from managers.tray_icon_manager import TrayIconManager
from managers.settings_manager import UserSettings
from utils.lava_lamp import LavaLampClient
import asyncio
from contextlib import suppress

user_settings = UserSettings()
sync_manager = SyncManager(user_settings)

# ===================== Main Loop =====================
async def main_loop() -> None:
    settle_delay_seconds = 1.6

    async with LavaLampClient("https://api.neurolavalamp.com") as client:
        pending_settle_task: asyncio.Task | None = None

        async def apply_settled_live_color() -> None:
            await asyncio.sleep(settle_delay_seconds)
            settled_state = await client.get_state()
            if settled_state.live:
                await asyncio.to_thread(sync_manager.update_color, settled_state.hex, True)

        async for state in client.stream_states():
            print(state.rgb_list, state.hex, state.live)

            if state.live:
                # Treat stream events as triggers: reschedule until updates settle.
                if pending_settle_task is not None and not pending_settle_task.done():
                    pending_settle_task.cancel()
                    with suppress(asyncio.CancelledError):
                        await pending_settle_task
                pending_settle_task = asyncio.create_task(apply_settled_live_color())
            else:
                # If lamp is not live, cancel pending settle and reset immediately.
                if pending_settle_task is not None and not pending_settle_task.done():
                    pending_settle_task.cancel()
                    with suppress(asyncio.CancelledError):
                        await pending_settle_task
                await asyncio.to_thread(sync_manager.update_color, state.hex, False)

        if pending_settle_task is not None and not pending_settle_task.done():
            pending_settle_task.cancel()
            with suppress(asyncio.CancelledError):
                await pending_settle_task
    # while True:
    #     sync_manager.update_color()


if __name__ == "__main__":
    tray_icon_manager = TrayIconManager(main_loop, user_settings, sync_manager)