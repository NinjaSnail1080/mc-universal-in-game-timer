"""
    Minecraft Universal In-Game Timer
    Copyright (C) 2020  NinjaSnail1080  (Discord User: @NinjaSnail1080#8581)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from PyQt5.QtCore import QRunnable, pyqtSlot, QObject, pyqtSignal
import rapidjson as json

import sys
import os


def get_default_minecraft_dir():
    if sys.platform == "win32":
        return os.path.join(os.environ["APPDATA"], ".minecraft")
    elif sys.platform == "darwin":
        return os.path.expanduser("~/Library/Application Support/minecraft/")
    else:
        return os.path.expanduser("~/.minecraft/")


def get_pre17_igt(mc_dir):
    if os.path.exists(os.path.join(mc_dir, "stats")):
        with open(os.path.join(mc_dir, "stats", os.listdir(os.path.join(mc_dir, "stats"))[0]), "r") as f:
            pre17_stats = json.load(f)
        return next(i for i in pre17_stats["stats-change"] if "1100" in i)["1100"]
    else:
        return 0


def set_theme_color(label, settings):
    if settings.value("Theme", "dark") == "dark":
        label.setStyleSheet("color: white;")
    else:
        label.setStyleSheet("color: black;")


def convert_hotkey(hotkey):
    all_hotkeys = []
    split_hotkey = hotkey.split(", ")

    for key in split_hotkey:
        if sys.platform == "darwin":
            key = key.lower().replace("ctrl", "cmd").replace("meta", "ctrl")

        key_list = key.split("+")
        for h in key_list.copy():
            if len(h) > 1:
                key_list[key_list.index(h)] = "<" + h + ">"
        all_hotkeys.append("+".join(key_list))

    return all_hotkeys


class WorkerSignals(QObject):
    result = pyqtSignal(object)


class Worker(QRunnable):
    def __init__(self, function):
        super(Worker, self).__init__()
        self.function = function
        self.signal = WorkerSignals()

    @pyqtSlot()
    def run(self):
        try:
            result = self.function()
            self.signal.result.emit(result)
        except:
            self.signal.result.emit(None)
