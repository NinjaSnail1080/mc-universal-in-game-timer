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

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic
from nbt.nbt import NBTFile
from pynput import keyboard
import rapidjson as json

import sys
import os
import time

import utils

try:
    DIRECTORY = sys._MEIPASS
except:
    DIRECTORY = os.path.dirname(__file__)

__version__ = open(os.path.join(DIRECTORY, "VERSION.txt")).read()

SETTINGS = QSettings(QSettings.NativeFormat, QSettings.UserScope, "Minecraft Universal In-Game Timer")

SETTINGS.setValue("ResetTime", utils.get_pre17_igt(SETTINGS.value("MinecraftDirectory", utils.get_default_minecraft_dir())))

#* Default Minecraft color codes (white and black omitted for obvious reasons)
MC_COLORS = {
    "dark_red": "#AA0000",
    "red": "#FF5555",
    "gold": "#FFAA00",
    "yellow": "#FFFF55",
    "dark_green": "#00AA00",
    "green": "#55FF55",
    "aqua": "#55FFFF",
    "dark_aqua": "#00AAAA",
    "dark_blue": "#0000AA",
    "blue": "#5555FF",
    "light_purple": "#FF55FF",
    "dark_purple": "#AA00AA",
    "gray": "#AAAAAA",
    "dark_gray": "555555"
}


def get_last_played_level():
    mc_dir = SETTINGS.value("MinecraftDirectory", utils.get_default_minecraft_dir())
    mc_saves = os.path.join(mc_dir, "saves")

    worlds_recently_modified = sorted([os.path.join(mc_saves, s) for s in os.listdir(mc_saves)], key=os.path.getmtime, reverse=True)
    for w in worlds_recently_modified.copy()[:3]:
        try:
            world = w
            level = NBTFile(os.path.join(world, "level.dat"))
            if not int(str(level["Data"]["Time"])):
                continue
            else:
                break
        except:
            continue

    try:
        with open(os.path.join(world, "stats", os.listdir(os.path.join(world, "stats"))[0]), "r") as f:
            stats = json.load(f)
    except: #* If it's pre 1.7.2
        stats = None

    try:
        seen_credits = bool(int(str(level["Data"]["Player"]["seenCredits"])))
    except: #* If it's pre 1.12 OR a server
        seen_credits = None

    try:
        data = {
            "name": str(level["Data"]["LevelName"]),
            "version": str(level["Data"]["Version"]["Name"]),
            "igt": stats["stat.playOneMinute"] if int(str(level["Data"]["DataVersion"])) < 1451 else stats["stats"]["minecraft:custom"]["minecraft:play_one_minute"],
            "seen_credits": seen_credits,
            "pre17": False
        }
    except: #* If it's pre 1.9
        try:
            data = {
                "name": str(level["Data"]["LevelName"]),
                "version": "Pre 1.9",
                "igt": stats["stat.playOneMinute"],
                "seen_credits": seen_credits,
                "pre17": False
            }
        except: #* If it's pre 1.7.2
            data = {
                "name": str(level["Data"]["LevelName"]),
                "version": "Pre 1.7.2",
                "igt": utils.get_pre17_igt(mc_dir),
                "seen_credits": seen_credits,
                "pre17": True
            }

    return data


class SettingsWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        uic.loadUi(os.path.join(DIRECTORY, "SettingsWindow.ui"), self)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.setWindowIcon(QIcon(os.path.join(DIRECTORY, "Resources", "icons.ico")))

        self.author_text.linkActivated.connect(self.open_link)
        self.author_text.setText(f"By NinjaSnail1080\u3000|\u3000<a href='https://github.com/NinjaSnail1080/mc-universal-in-game-timer'>Github</a> (v{__version__})")

        self.browse_field.setText(SETTINGS.value("MinecraftDirectory", utils.get_default_minecraft_dir()))
        self.browse_field.setFocus()
        self.browse_button.clicked.connect(self.browse_for_mc_dir)

        if bool(int(SETTINGS.value("IGTTimer", 1))):
            self.igt_timer_check.setChecked(True)
        if bool(int(SETTINGS.value("RTATimer", 0))):
            self.rta_timer_check.setChecked(True)
        if bool(int(SETTINGS.value("ShowWorldName", 1))):
            self.world_name_check.setChecked(True)
        if bool(int(SETTINGS.value("ShowHours", 1))):
            self.hours_check.setChecked(True)

        if bool(int(SETTINGS.value("AutoStartRTA", 0))):
            self.auto_start_check.setChecked(True)
        if bool(int(SETTINGS.value("AutoStopTimers", 0))):
            self.auto_stop_check.setChecked(True)

        if SETTINGS.value("RTAHotkey", None) is None:
            self.rta_hotkey = None
        else:
            self.rta_hotkey = SETTINGS.value("RTAHotkey")
            self.set_rta_hotkey.setKeySequence(self.rta_hotkey)
        self.set_rta_hotkey.keySequenceChanged.connect(self.change_rta_hotkey)

        if SETTINGS.value("RTAResetHotkey", None) is None:
            self.rta_reset_hotkey = None
        else:
            self.rta_reset_hotkey = SETTINGS.value("RTAResetHotkey")
            self.set_rta_reset_hotkey.setKeySequence(self.rta_reset_hotkey)
        self.set_rta_reset_hotkey.keySequenceChanged.connect(self.change_rta_reset_hotkey)

        self.opacity_slider.setMinimum(10)
        self.opacity_slider.setMaximum(100)
        self.opacity_slider.setSingleStep(1)
        self.opacity_slider.setTickInterval(10)
        self.opacity_slider.setTickPosition(QSlider.TicksBothSides)
        self.opacity_slider.valueChanged.connect(self.change_opacity_percentage)
        self.opacity_slider.setValue(int(float(SETTINGS.value("Opacity", 0.5))*100))

        if SETTINGS.value("Theme", "dark") == "dark":
            self.dark_theme_button.setChecked(True)
        else:
            self.light_theme_button.setChecked(True)

        self.continue_button.setText("Save")
        self.continue_button.clicked.connect(self.save_and_exit_settings)

        frame = self.frameGeometry()
        screen = QDesktopWidget().primaryScreen()
        screen_center = QDesktopWidget().screenGeometry(screen).center()
        frame.moveCenter(screen_center)
        self.move(frame.topLeft())

        self.setFixedSize(430, 530)
        self.show()

    def browse_for_mc_dir(self):
        browse = QFileDialog(self)
        browse.setFileMode(QFileDialog.DirectoryOnly)
        if browse.exec_():
            mc_dir = browse.selectedFiles()[0]
            self.browse_field.setText(mc_dir)

    def change_opacity_percentage(self):
        self.opacity_text.setText(f"Opacity: {self.opacity_slider.value()}%")

    def open_link(self, link):
        QDesktopServices.openUrl(QUrl(link))

    def change_rta_hotkey(self):
        self.rta_hotkey = self.set_rta_hotkey.keySequence().toString()

    def change_rta_reset_hotkey(self):
        self.rta_reset_hotkey = self.set_rta_reset_hotkey.keySequence().toString()

    def save_and_exit_settings(self):
        if self.browse_field.text() == "":
            SETTINGS.setValue("MinecraftDirectory", utils.get_default_minecraft_dir())
        else:
            SETTINGS.setValue("MinecraftDirectory", self.browse_field.text())

        SETTINGS.setValue("IGTTimer", int(self.igt_timer_check.isChecked()))
        SETTINGS.setValue("RTATimer", int(self.rta_timer_check.isChecked()))
        SETTINGS.setValue("ShowWorldName", int(self.world_name_check.isChecked()))
        SETTINGS.setValue("ShowHours", int(self.hours_check.isChecked()))
        SETTINGS.setValue("AutoStartRTA", int(self.auto_start_check.isChecked()))
        SETTINGS.setValue("AutoStopTimers", int(self.auto_stop_check.isChecked()))

        SETTINGS.setValue("RTAHotkey", self.rta_hotkey)
        SETTINGS.setValue("RTAResetHotkey", self.rta_reset_hotkey)

        SETTINGS.setValue("Opacity", self.opacity_slider.value() / 100)

        if self.dark_theme_button.isChecked():
            SETTINGS.setValue("Theme", "dark")
        elif self.light_theme_button.isChecked():
            SETTINGS.setValue("Theme", "light")

        self.close()
        self.new = TimerWindow()
        self.new.show()


class TimerWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setWindowOpacity(float(SETTINGS.value("Opacity", 0.5)))
        self.setWindowIcon(QIcon(os.path.join(DIRECTORY, "Resources", "icons.ico")))

        self.threadpool = QThreadPool()

        #*I have to do it in this weird, convoluted way because the sane way doesn't work for some reason
        with open(os.path.join(DIRECTORY, "Resources", "Minecraftia-Regular-1.ttf"), "rb") as f:
            self.small_font = QFont(QFontDatabase.applicationFontFamilies(QFontDatabase.addApplicationFontFromData(f.read()))[0], 12)
        with open(os.path.join(DIRECTORY, "Resources", "Minecraftia-Regular-2.ttf"), "rb") as f:
            self.medium_font = QFont(QFontDatabase.applicationFontFamilies(QFontDatabase.addApplicationFontFromData(f.read()))[0], 24)
        with open(os.path.join(DIRECTORY, "Resources", "Minecraftia-Regular-3.ttf"), "rb") as f:
            self.large_font = QFont(QFontDatabase.applicationFontFamilies(QFontDatabase.addApplicationFontFromData(f.read()))[0], 30)

        self.igt_timer = QTimer()
        self.igt_timer.setTimerType(Qt.PreciseTimer)
        self.igt_timer.timeout.connect(self.update_igt)

        self.rta_timer = QTimer()
        self.rta_timer.setTimerType(Qt.PreciseTimer)
        self.rta_timer.timeout.connect(self.update_rta)

        if bool(int(SETTINGS.value("ShowHours", 1))):
            self.rta = QLabel("00:00:00.000")
        else:
            self.rta = QLabel("00:00.000")
        self.rta.setAlignment(Qt.AlignCenter)
        self.rta.setStyleSheet(f"color: {MC_COLORS['red']};")
        if bool(int(SETTINGS.value("IGTTimer", 1))):
            self.rta.setFont(self.large_font)
        else:
            self.rta.setFont(self.medium_font)

        if bool(int(SETTINGS.value("ShowHours", 1))):
            self.igt = QLabel("--:--:--.---")
        else:
            self.igt = QLabel("--:--.---")
        self.igt.setAlignment(Qt.AlignCenter)
        utils.set_theme_color(self.igt, SETTINGS)
        self.igt.setFont(self.medium_font)

        self.right_click_text = QLabel("Right-click to reset IGT")
        self.right_click_text.setAlignment(Qt.AlignCenter)
        utils.set_theme_color(self.right_click_text, SETTINGS)
        self.right_click_text.setFont(self.small_font)

        self.toolbar = QToolBar("Main toolbar")
        self.toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(self.toolbar)

        if SETTINGS.value("Theme", "dark") == "dark":
            self.close_button = QAction(QIcon(os.path.join(DIRECTORY, "Resources", "white_x")), "", self)
            self.settings_button = QAction(QIcon(os.path.join(DIRECTORY, "Resources", "white_gear")), "", self)
        else:
            self.close_button = QAction(QIcon(os.path.join(DIRECTORY, "Resources", "black_x")), "", self)
            self.settings_button = QAction(QIcon(os.path.join(DIRECTORY, "Resources", "black_gear")), "", self)
        self.close_button.triggered.connect(self.close_window)
        self.settings_button.triggered.connect(self.open_settings)

        self.world_name = QLabel("Searching...")
        utils.set_theme_color(self.world_name, SETTINGS)
        self.world_name.setFont(self.small_font)

        self.left_spacer = QWidget()
        self.left_spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.right_spacer = QWidget()
        self.right_spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.toolbar.addAction(self.close_button)
        self.toolbar.addWidget(self.left_spacer)
        self.toolbar.addWidget(self.world_name)
        self.toolbar.addWidget(self.right_spacer)
        self.toolbar.addAction(self.settings_button)
        self.toolbar.setMovable(False)
        self.toolbar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.toolbar.setStyleSheet("border: none;")

        self.widget_layout = QVBoxLayout()
        if bool(int(SETTINGS.value("RTATimer", 0))):
            self.widget_layout.addWidget(self.rta)
        if bool(int(SETTINGS.value("IGTTimer", 1))):
            self.widget_layout.addWidget(self.igt)
        self.widget_layout.addWidget(self.right_click_text)
        self.right_click_text.hide()
        self.main_widget = QWidget()
        self.main_widget.setLayout(self.widget_layout)
        self.setCentralWidget(self.main_widget)

        if SETTINGS.value("Theme", "dark") == "dark":
            self.setStyleSheet("background-color: black;")
        else:
            self.setStyleSheet("background-color: white;")
        self.move(int(SETTINGS.value("TimerPosX", 0)), int(SETTINGS.value("TimerPosY", 0)))

        self.right_clicked = False
        self.reset = False
        self.stop_timer = True
        self.timestamp_ms = round(time.time() * 1000)
        self.stopped_time_at = self.timestamp_ms
        self.stopped_time = 0
        self.stopped_rta_after_credits = False

        self.global_hotkey_listener = None

        self.show()

        if not bool(int(SETTINGS.value("IGTTimer", 1))) and not bool(int(SETTINGS.value("ShowWorldName", 1))):
            self.world_name.setText("")
        else:
            self.igt_timer.start(50)

        if bool(int(SETTINGS.value("RTATimer", 0))):
            rta_hotkey = SETTINGS.value("RTAHotkey", None)
            rta_reset_hotkey = SETTINGS.value("RTAResetHotkey", None)
            global_hotkeys = {}

            if rta_hotkey:
                for hotkey in utils.convert_hotkey(rta_hotkey):
                    global_hotkeys.update({hotkey: self.rta_hotkey_pressed})
            if rta_reset_hotkey:
                for hotkey in utils.convert_hotkey(rta_reset_hotkey):
                    global_hotkeys.update({hotkey: self.rta_reset_hotkey_pressed})

            if global_hotkeys:
                self.global_hotkey_listener = keyboard.GlobalHotKeys(global_hotkeys)
                self.global_hotkey_listener.start()

            self.rta_timer.start(1)

    def update_igt(self):

        def update_after_thread_complete(level_data):
            try:
                if bool(int(SETTINGS.value("ShowWorldName", 1))):
                    self.world_name.setText(f"{level_data['name']} ({level_data['version']})")
                    utils.set_theme_color(self.world_name, SETTINGS)
                else:
                    self.world_name.setText("")

                if bool(int(SETTINGS.value("AutoStartRTA", 1))):
                    if level_data["igt"] <= 5 and self.reset == False:
                        self.reset = True
                        self.stop_timer = False
                        self.rta_reset_hotkey_pressed()

                    if level_data["igt"] > 5 and self.reset == True:
                        self.reset = False

                if level_data["seen_credits"] and bool(int(SETTINGS.value("AutoStopTimers", 0))):
                    if not self.stopped_rta_after_credits:
                        if not self.stop_timer:
                            self.rta_hotkey_pressed()
                        self.stopped_rta_after_credits = True
                    self.igt.setStyleSheet(f"color: {MC_COLORS['blue']};")
                    utils.set_theme_color(self.world_name, SETTINGS)
                    self.setFixedWidth(max([self.toolbar.sizeHint().width(), self.widget_layout.sizeHint().width()]) + 16)
                    return
                else:
                    self.stopped_rta_after_credits = False

                if level_data["pre17"]:
                    self.right_click_text.show()
                    if self.right_clicked:
                        SETTINGS.setValue("ResetTime", level_data["igt"])
                        self.right_clicked = False
                    ticks = level_data["igt"] - int(SETTINGS.value("ResetTime"))
                else:
                    self.right_click_text.hide()
                    self.resize(self.sizeHint())
                    ticks = level_data["igt"]

                seconds = ticks // 20
                h = str(seconds // 60 // 60)
                m = str(seconds // 60 % 60)
                s = str(seconds % 60)
                ms = str(int(ticks % 20 / 2 * 100))

                if bool(int(SETTINGS.value("ShowHours", 1))):
                    self.igt.setText(f"{h.zfill(2)}:{m.zfill(2)}:{s.zfill(2)}.{ms.zfill(3)}")
                else:
                    self.igt.setText(f"{m.zfill(2)}:{s.zfill(2)}.{ms.zfill(3)}")
                utils.set_theme_color(self.igt, SETTINGS)
                self.setFixedWidth(max([self.toolbar.sizeHint().width(), self.widget_layout.sizeHint().width()]) + 16)
            except:
                self.world_name.setText("ERROR:  No World Found")
                self.world_name.setStyleSheet("color: red;")
                if bool(int(SETTINGS.value("ShowHours", 1))):
                    self.igt.setText("--:--:--.---")
                else:
                    self.igt.setText("--:--.---")
                utils.set_theme_color(self.igt, SETTINGS)
                self.setFixedWidth(max([self.toolbar.sizeHint().width(), self.widget_layout.sizeHint().width()]) + 16)

        worker = utils.Worker(get_last_played_level)
        worker.signal.result.connect(update_after_thread_complete)
        self.threadpool.start(worker)

    def update_rta(self):
        if self.stop_timer:
            self.rta.setStyleSheet(f"color: {MC_COLORS['red']};")
            return

        if SETTINGS.value("Theme", "dark") == "dark":
            self.rta.setStyleSheet(f"color: {MC_COLORS['green']};")
        else:
            self.rta.setStyleSheet(f"color: {MC_COLORS['dark_green']};")

        milliseconds = round(time.time() * 1000) - self.timestamp_ms - self.stopped_time
        seconds = milliseconds // 1000
        h = str(seconds // 60 // 60)
        m = str(seconds // 60 % 60)
        s = str(seconds % 60)
        ms = str(int(milliseconds % 1000))

        if bool(int(SETTINGS.value("ShowHours", 1))):
            self.rta.setText(f"{h.zfill(2)}:{m.zfill(2)}:{s.zfill(2)}.{ms.zfill(3)}")
        else:
            self.rta.setText(f"{m.zfill(2)}:{s.zfill(2)}.{ms.zfill(3)}")

    def rta_hotkey_pressed(self):
        if self.stop_timer:
            self.stopped_time += (round(time.time() * 1000) - self.stopped_time_at)
            self.stop_timer = False
        else:
            self.stopped_time_at = round(time.time() * 1000)
            self.stop_timer = True

    def rta_reset_hotkey_pressed(self):
        self.timestamp_ms = round(time.time() * 1000)
        if self.stop_timer:
            self.stopped_time_at = round(time.time() * 1000)
        self.stopped_time = 0
        if bool(int(SETTINGS.value("ShowHours", 1))):
            self.rta.setText("00:00:00.000")
        else:
            self.rta.setText("00:00.000")

    def close_window(self):
        SETTINGS.setValue("TimerPosX", self.x())
        SETTINGS.setValue("TimerPosY", self.y())
        if self.global_hotkey_listener:
            self.global_hotkey_listener.stop()
        self.igt_timer.stop()
        self.rta_timer.stop()
        self.threadpool.clear()
        self.close()

    def open_settings(self):
        self.close_window()
        self.setStyleSheet("")
        SettingsWindow(self)

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()
        if event.button() == Qt.RightButton:
            self.right_clicked = True

    def mouseMoveEvent(self, event):
        try:
            delta = QPoint(event.globalPos() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPos()
        except AttributeError:
            pass


if __name__ == "__main__":
    app = QApplication([])
    if sys.platform == "darwin":
        app.setStyle(QStyleFactory.create("macintosh"))
    else:
        app.setStyle(QStyleFactory.create("Fusion"))

    window = TimerWindow()
    app.exec_()
    sys.exit()
