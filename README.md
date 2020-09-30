# Minecraft Universal In-Game Timer
**An open-source, cross-platform, in-game timer for Minecraft speedrunners**

Copyright © 2020 NinjaSnail1080 (Discord User: @NinjaSnail1080#8581)

Licensed under the GNU General Public License v3.0. See LICENSE.txt for details

---

Minecraftia font by [Andrew Tyler](https://ajtyler.co/)

Ender Dragon icon from the [Minecraft Wiki](https://minecraft.gamepedia.com/Minecraft_Wiki)

---

### [Download for your OS here](https://github.com/NinjaSnail1080/mc-universal-in-game-timer/releases) (Windows, MacOS, and Linux)

### Works in every single Minecraft version since 1.0!

### [Here's a video](https://www.youtube.com/watch?v=fPESBmKYi0Q) showing how it works

## Usage
Click the X in the top-left corner to close the timer.

Click the gear icon in the top-right corner to view the settings, where you can edit the opacity of the timer, set your Minecraft directory, choose which timers you want to use, etc.

There are two timers built into this app. One shows in-game time (IGT), and the other shows real time (RTA). The RTA timer is controlled by hotkeys that you can set in the timer settings.

If you're using a version before 1.7.2, the IGT timer will not keep track of the in-game time for a specific world because of how the game handled stats back then. So, you'll have to manually reset the timer by right-clicking on it before starting a new world.

The IGT timer will appear frozen because due to how Minecraft stores its in-game time, it only updates when the game saves. It will update every 5 minutes on autosaves, every time you open the pause menu, and when you go through the exit portal in the End. If you're using a version before 1.7.2, it'll also update every 5 seconds.

If you don't use the default Minecraft directory, then you'll have to go into the timer's settings and set it to the directory that you do use.

If the IGT timer doesn't update when you make a new world, then there are two possibilities. One is that you migrated your Minecraft directory, but the old one still exists and that's where the timer is reading from. Change your directory to the correct one in the timer's settings.

Here's the other possibility: In some Minecraft versions, the IGT timer won't update on its own when you make a new world. It will still update on saves, so pressing `esc` twice to pause and unpause the game should cause the timer to show the correct world and time.

The timer reads the in-game time from the world (1.7.2+) or game (1.6.4 and earlier) statistics file, so it will always show an accurate time.

**Note**: For some people on macOS, the timer will crash if you set hotkeys.  If this happens to you, you can reset your hotkeys as follows:

1. Open Terminal
2. Run `rm ~/Library/Preferences/com.minecraft-universal-in-game-timer.plist`
3. Run `killall cfprefsd`

You should be able to open the timer again, provided that you don't attempt to set hotkeys again.

If you still experience issues or have any other questions, you can message me on Discord at NinjaSnail1080#8581 or [open an issue here](https://github.com/NinjaSnail1080/mc-universal-in-game-timer/issues).

---

That's about it. Good luck with your speedrun!
