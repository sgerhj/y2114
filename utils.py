import logging
import subprocess
import os
import sys
from time import sleep

import keyboard
import mouse
import pyautogui
from win32gui import FindWindow, GetWindowRect

log = logging.getLogger(__name__)

# WINDOW NAMES
LEAGUE_CLIENT_WINNAME = "League of Legends"
LEAGUE_GAME_CLIENT_WINNAME = "League of Legends (TM) Client"

# PROCESS NAMES
LEAGUE_PROCESS_NAMES = ["LeagueClient.exe", "League of Legends.exe"]
RIOT_CLIENT_PROCESS_NAMES = ["RiotClientUx.exe", "RiotClientServices.exe", "Riot Client.exe"]

# COMMANDS
KILL_CRASH_HANDLER = 'TASKKILL /F /IM LeagueCrashHandler64.exe'
KILL_LEAGUE_CLIENT = 'TASKKILL /F /IM LeagueClient.exe'
KILL_LEAGUE = 'TASKKILL /F /IM "League of Legends.exe"'
KILL_RIOT_CLIENT = 'TASKKILL /F /IM RiotClientUx.exe'
KILL_HANDLER_WMIC = 'wmic process where "name=\'LeagueCrashHandler64.exe\'" delete'
KILL_LEAGUE_WMIC = 'wmic process where "name=\'LeagueClient.exe\'" delete'

RIOT_LOCKFILE = 'D:\Games\Riot Games\Riot Client\RiotClientServices.exe'
LEAGUE_LOCKFILE = 'D:\Games\Riot Games\League of Legends\LeagueClient.exe'


class WindowNotFound(Exception):
    pass


def is_league_process_running() -> bool:
    """Returns boolean if league process is found"""
    output = subprocess.run("tasklist", capture_output=True, text=True).stdout
    for name in LEAGUE_PROCESS_NAMES:
        if name in output:
            return True
    return False


def exists(window_name: str) -> bool:
    """Returns boolean if window is found"""
    return FindWindow(None, window_name) != 0


def get_window_rect(window_name: str) -> tuple:
    """Gets window rect given a window name"""
    hwnd = FindWindow(None, window_name)
    if not hwnd:
        raise WindowNotFound(f"{window_name} not found")
    return GetWindowRect(hwnd)


def click(coords: tuple, window_name: str) -> None:
    """Clicks on specified coords of window"""
    log.debug(f"Clicking {coords} on {window_name}")
    hwnd = FindWindow(None, window_name)
    if not hwnd:
        raise WindowNotFound(f"{window_name} not found")

    left, top, right, bottom = GetWindowRect(hwnd)
    x = int(left + (right - left) * coords[0])
    y = int(top + (bottom - top) * coords[1])

    pyautogui.click(x, y)


def press(key: str, window_name: str) -> None:
    """Presses specified key"""
    log.debug(f"Pressing {key} on {window_name}")
    hwnd = FindWindow(None, window_name)
    if not hwnd:
        raise WindowNotFound(f"{window_name} not found")

    pyautogui.press(key)


def attack_move_click(coords: tuple) -> None:
    """Performs attack move click on specified coordinates"""
    log.debug(f"Attack move click at {coords}")
    press('a', LEAGUE_GAME_CLIENT_WINNAME)
    sleep(0.1)
    click(coords, LEAGUE_GAME_CLIENT_WINNAME)
