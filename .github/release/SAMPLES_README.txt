@# The README of every sample download (D-40 RS). .github/scripts/package_sample.py writes it into each download as
@# README.txt: lines starting with "@#" are dropped, "@only PLATFORM ..." keeps the lines up to "@end" only in the
@# downloads named (gba, linux-x86_64, windows-x64, macos-universal), and {version} becomes the release's version.
CapsuleCreatures samples {version}
==================================

Two small programs built with the CapsuleCreatures engine, using only its own neutral sample data and art made
of simple shapes:

- Starter Battle (capsule_starter_battle): the Starter sample game's battles. Fight three rivals or unowned
  creatures in 1 vs 1 and 2 vs 2, recruit creatures with Orbs, heal with Tonics, look into the storage boxes,
  or watch a double battle played by the AI on both sides.
- Map Sandbox (capsule_sandbox_map): the overworld. Walk Showcase Park, a meadow and a dark cave, talk to the
  people there, read signs, ride the warps with their screen transitions, wade across the pond and light the
  cave with the Starter's field actions. It is the engine's map sandbox, so it also has a debug overlay
  (hidden at start; SELECT turns it on and off) and a noclip mode. It has no battles: an encounter in the
  grass is listed on the overlay and the walk goes on.

The same programs run on the Game Boy Advance and on Linux, Windows and macOS; each download holds one platform.

Controls
--------
@only gba
  GBA button      What it does
  D-pad           move the cursor (moves: past a page's edge to the next four) / walk
  A               choose / talk, read a sign
  B               back / run
  START           Map Sandbox: the menu (go to a map, night on / off, the field action, ...)
  SELECT          Starter Battle: the About page (on the first menu); Map Sandbox: the debug overlay on / off
                  while walking, the About page in the START menu
  L / R           Starter Battle: previous / next storage box; Map Sandbox: collision view / noclip
@end
@only linux-x86_64 windows-x64 macos-universal
  Key             GBA button   What it does
  Arrow keys      D-pad        move the cursor (moves: past a page's edge to the next four) / walk
  X               A            choose / talk, read a sign
  Z               B            back / run (hold it while walking)
  Enter           START        Map Sandbox: the menu (go to a map, night on / off, the field action, ...)
  Backspace       SELECT       Starter Battle: the About page (on the first menu); Map Sandbox: the debug
                               overlay on / off while walking, the About page in the START menu
  Q / W           L / R        Starter Battle: previous / next storage box; Map Sandbox: collision view / noclip
  (S and A are the X and Y buttons; the samples do not use them.)

The window can be resized; the picture keeps the GBA's 240 x 160 pixels, scaled by whole steps.
@end

How to run
----------
@only gba
The ROMs are capsule_starter_battle.gba and capsule_sandbox_map.gba.

On an emulator: open the .gba file in mGBA (https://mgba.io), File > Load ROM, or drag it onto the mGBA window.
No BIOS file is needed. Other accurate GBA emulators work too.

On hardware: copy the .gba file to a GBA flash cartridge's memory card and start it from the cartridge's menu.
Each ROM is far smaller than the cartridge it targets (8 MB) and does not save, so any save-type setting works.
The header carries a valid checksum (gbafix), a title (STARTER / MAP SANDBOX) and its own game code.
@end
@only linux-x86_64
Unpack the archive, then double-click capsule_starter_battle or capsule_sandbox_map in your file manager (or run
./capsule_starter_battle from a terminal in this folder). If the file manager opens them as text or does nothing,
right-click > Properties > Permissions > "Allow executing file as program", or run chmod +x on them.

The programs need an x86_64 Linux with glibc 2.28 or newer (Debian 10, Ubuntu 20.04, Fedora 29, RHEL 8 or any
current rolling distribution such as Arch, CachyOS or openSUSE Tumbleweed) and an X11 or Wayland desktop. Sound
plays through PipeWire, PulseAudio or ALSA, whichever is there. Nothing else needs installing: SDL2 and the C++
runtime are built in.
@end
@only windows-x64
Unzip the download first (right-click > Extract All...), then double-click capsule_starter_battle.exe or
capsule_sandbox_map.exe. They need 64-bit Windows 10 or 11 and nothing else (no DLLs, no installer).

The programs are not signed, so Windows SmartScreen may say "Windows protected your PC". Click "More info", then
"Run anyway". This is asked once per program.

They open no console window. To see their log lines (for a bug report), start one from Command Prompt or
PowerShell in this folder: .\capsule_starter_battle.exe
@end
@only macos-universal
Unzip the download (double-click it), then open "Starter Battle.app" or "Map Sandbox.app". They run on macOS
10.15 or newer, on Apple silicon and Intel Macs alike (universal).

The apps are not signed by an identified developer or notarised by Apple, so the first open is refused with
"cannot be opened because Apple cannot check it for malicious software" (or "... is from an unidentified
developer"). To open one anyway:
  1. Double-click the app once and close the message (Done or OK).
  2. Open System Settings > Privacy & Security, scroll down to Security and click "Open Anyway" beside the
     app's name, then confirm with your password and "Open". (macOS 14 and older: you can instead Control-click
     the app in Finder, choose Open, then Open again.)
macOS remembers the choice; later opens work normally. Moving the app to the Applications folder is optional.

If macOS says the app "is damaged and can't be opened", the download lost its signature on the way (some unzip
tools do this). Unzip it with Finder, or run this in Terminal in the folder that holds the app:
  xattr -dr com.apple.quarantine "Starter Battle.app"

Log lines (for a bug report): run the program inside the app from Terminal,
  "./Starter Battle.app/Contents/MacOS/capsule_starter_battle"
@end

What is in this download
------------------------
@only gba
  capsule_starter_battle.gba, capsule_sandbox_map.gba   the ROMs
@end
@only linux-x86_64
  capsule_starter_battle, capsule_sandbox_map           the programs
@end
@only windows-x64
  capsule_starter_battle.exe, capsule_sandbox_map.exe   the programs
@end
@only macos-universal
  Starter Battle.app, Map Sandbox.app                   the programs
@end
  README.txt                                            this file
  LICENSE                                               the engine's licence (MPL-2.0)
  THIRD_PARTY_NOTICES.md                                the licences of the parts built into the programs

Credits
-------
Made with the CapsuleCreatures engine (https://github.com/TheWildDeadHero/CapsuleCreatures), MPL-2.0. The
Starter sample's creatures, moves, numbers and art are the engine's own, made for the sample.
@only gba
The GBA build is based in part on the work of devkitPro (https://devkitpro.org): it links devkitPro's libgba and
devkitARM's start-up code, built with devkitARM. libgba is used under the LGPL with its static-linking exception;
newlib's notices are in the third-party file.
@end
@only linux-x86_64 windows-x64 macos-universal
The desktop builds use SDL2 (https://libsdl.org, zlib licence), built into the programs.
The GBA builds of the same samples are based in part on the work of devkitPro (https://devkitpro.org).
@end

The source, the toolkit (editors and the build setup) and the getting-started guide are in the repository above.
To change a sample, open it in the Studio as a project of your own: Open a sample... copies it into a folder you
choose (the getting-started guide's step A6), and ./build PRESET --game FOLDER builds the copy.
