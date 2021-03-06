import json
from functools import partial
from itertools import chain
from pathlib import Path
from typing import Callable, Iterable, Optional

from kivy import Logger

_SETTINGS_PLUGIN_DATA = None


def _has_rpi_backlight() -> bool:
    BL_DIR = Path("/") / "sys" / "class" / "backlight" / "rpi_backlight" / "bl_power"
    if not BL_DIR.exists():
        Logger.debug(f"rpi_backlight: {BL_DIR} does not exist")
        return False
    # Check if we can read/write
    try:
        val = int(BL_DIR.read_bytes())
        BL_DIR.write_bytes(bytes(val))
        Logger.debug(f"rpi_backlight: Has backlight")
        return True
    except (PermissionError, ValueError) as e:
        Logger.info(f"rpi_backlight: Path exists but got - {e}")
        return False


def _generate_screen_saver_dict(checker: Callable[[], bool]) -> list[dict]:
    if checker():
        return [
            dict(
                type="bool",
                title="ScreenSaver",
                desc="Enable a ScreenSaver",
                section="Plugins",
                key="SCREEN_SAVER_ENABLE",
            ),
            dict(
                type="numeric",
                title="ScreenSaver Delay",
                desc="Enable ScreenSaver after this many minutes",
                section="Plugins",
                key="SCREEN_SAVER_DELAY",
            ),
        ]


def _generate_plugin_json(
    plugin_generators: Iterable[Callable[[], Optional[list[dict]]]]
) -> str:
    data = []
    for p in plugin_generators:
        p_data = p()
        if p_data:
            data.extend(p_data)
    return json.dumps(data)


def _load_plugin_settings():
    global _SETTINGS_PLUGIN_DATA
    if _SETTINGS_PLUGIN_DATA is not None:
        return _SETTINGS_PLUGIN_DATA

    generate_screen_saver_dict = partial(
        _generate_screen_saver_dict, checker=_has_rpi_backlight
    )
    generate_plugin_json = partial(
        _generate_plugin_json, plugin_generators=(generate_screen_saver_dict,)
    )
    _SETTINGS_PLUGIN_DATA = generate_plugin_json()
    return _SETTINGS_PLUGIN_DATA


def __getattr__(name):
    if name == "SETTINGS_PLUGIN_DATA":
        return _load_plugin_settings()
    elif name == "_generate_plugin_json":
        return _generate_plugin_json
    elif name == "_generate_screen_saver_dict":
        return _generate_screen_saver_dict
    elif name == "_has_rpi_backlight":
        return _has_rpi_backlight
    else:
        raise AttributeError
