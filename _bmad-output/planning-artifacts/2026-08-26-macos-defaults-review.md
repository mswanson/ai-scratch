# macOS Defaults — Settings Review

Generated from `scripts/setup-macos-defaults.sh` at commit `0a4608d`. 69 settings,
down from 85 after the first cull. Every domain is verified to exist on macOS 26.

Comment on any block to cut, change, or ask about it. Nothing here has been
applied to the machine yet: the script prompts and defaults to No.

**Five that will visibly change the machine**, so notice them before rather than
after: **23** (⌘Q quits Finder, which also hides desktop icons while it is quit),
**28** (show hidden files everywhere, permanently), **40/41/42** (Dock icons to
48px with magnification to 64), **18** (screenshots to Desktop, which moves them
if yours currently go elsewhere), and **66** (Terminal SecureKeyboardEntry, which
can break password-manager autofill into Terminal).

---


## General UI/UX

**1.** `NSGlobalDomain AppleShowScrollBars -string "WhenScrolling"`  
Scrollbars appear only while scrolling, then fade. The alternatives are `Automatic` and `Always`.

**2.** `NSGlobalDomain NSTableViewDefaultSizeMode -int 2`  
medium sidebar icons

**3.** `NSGlobalDomain NSWindowResizeTime -float 0.001`  
instant window resize

**4.** `NSGlobalDomain NSNavPanelExpandedStateForSaveMode -bool true`  
Save dialogs open in the expanded browser view, not the one-line collapsed one.

**5.** `NSGlobalDomain NSNavPanelExpandedStateForSaveMode2 -bool true`  
Save dialogs open in the expanded browser view, not the one-line collapsed one.

**6.** `NSGlobalDomain PMPrintingExpandedStateForPrint -bool true`  
Print dialogs open expanded, showing all options rather than the summary.

**7.** `NSGlobalDomain PMPrintingExpandedStateForPrint2 -bool true`  
Print dialogs open expanded, showing all options rather than the summary.

**8.** `NSGlobalDomain NSDocumentSaveNewDocumentsToCloud -bool false`  
save to disk, not iCloud


## Text input: every one of these exists because they corrupt code

**9.** `NSGlobalDomain NSAutomaticCapitalizationEnabled -bool false`  
Stop auto-capitalising the first word of a sentence.

**10.** `NSGlobalDomain NSAutomaticDashSubstitutionEnabled -bool false`  
Stop turning `--` into an em dash. This one silently corrupts CLI flags.

**11.** `NSGlobalDomain NSAutomaticPeriodSubstitutionEnabled -bool false`  
Stop turning a double space into a period.

**12.** `NSGlobalDomain NSAutomaticQuoteSubstitutionEnabled -bool false`  
Stop turning straight quotes into curly ones. Breaks pasted code and JSON.

**13.** `NSGlobalDomain NSAutomaticSpellingCorrectionEnabled -bool false`  
Turn off autocorrect system-wide.


## Keyboard

**14.** `NSGlobalDomain KeyRepeat -int 2`  
How fast a held key repeats. 2 is fast; the Settings slider bottoms out at 2.

**15.** `NSGlobalDomain InitialKeyRepeat -int 15`  
How long before a held key starts repeating. 15 is ~225ms; the slider stops at 15.

**16.** `NSGlobalDomain AppleKeyboardUIMode -int 3`  
full keyboard access

**17.** `NSGlobalDomain ApplePressAndHoldEnabled -bool false`  
key repeat, not accent menu


## Screenshots

**18.** `com.apple.screencapture location -string "${HOME}/Desktop"`  
Where screenshots land. This is the default already; it matters on a machine where it was changed.

**19.** `com.apple.screencapture type -string "png"`  
Screenshot format. PNG over JPG for text legibility.

**20.** `com.apple.screencapture disable-shadow -bool true`  
Drop the large drop shadow around window screenshots. Makes them crop cleanly.


## Screen lock

**21.** `com.apple.screensaver askForPassword -int 1`  
Require a password after sleep or screensaver.

**22.** `com.apple.screensaver askForPasswordDelay -int 0`  
Require it immediately, with no grace period.


## Finder

**23.** `com.apple.finder QuitMenuItem -bool true`  
⌘Q quits Finder

**24.** `com.apple.finder ShowHardDrivesOnDesktop -bool false`  
Hide the internal drive icon on the desktop.

**25.** `com.apple.finder ShowExternalHardDrivesOnDesktop -bool true`  
Show external drives on the desktop.

**26.** `com.apple.finder ShowMountedServersOnDesktop -bool false`  
Hide mounted network shares on the desktop.

**27.** `com.apple.finder ShowRemovableMediaOnDesktop -bool true`  
Show USB sticks and SD cards on the desktop.

**28.** `com.apple.finder AppleShowAllFiles -bool true`  
show hidden files

**29.** `NSGlobalDomain AppleShowAllExtensions -bool true`  
Always show file extensions, everywhere.

**30.** `com.apple.finder ShowStatusBar -bool true`  
Finder status bar: item count and free space at the bottom of the window.

**31.** `com.apple.finder ShowPathbar -bool true`  
Finder path bar: the breadcrumb trail at the bottom of the window.

**32.** `com.apple.finder _FXShowPosixPathInTitle -bool true`  
Put the full POSIX path in the Finder window title instead of just the folder name.

**33.** `com.apple.finder _FXSortFoldersFirst -bool true`  
Folders sort above files rather than interleaved alphabetically.

**34.** `com.apple.finder FXDefaultSearchScope -string "SCcf"`  
search current folder

**35.** `com.apple.finder FXEnableExtensionChangeWarning -bool false`  
Stop the 'are you sure you want to change the extension' dialog.

**36.** `com.apple.finder FXPreferredViewStyle -string "Nlsv"`  
list view

**37.** `NSGlobalDomain com.apple.springing.enabled -bool true`  
Spring-loaded folders: hold a dragged file over a folder and it opens.

**38.** `NSGlobalDomain com.apple.springing.delay -float 0`  
No delay before that happens.

**39.** `com.apple.finder FXInfoPanesExpanded -dict  (General, OpenWith, Privileges)`  
Expand File Info panes: General, Open with, Sharing & Permissions.


## Dock and Mission Control

**40.** `com.apple.dock tilesize -int 48`  
Dock icon size in pixels.

**41.** `com.apple.dock magnification -bool true`  
Dock icons grow on hover.

**42.** `com.apple.dock largesize -int 64`  
How big they grow.

**43.** `com.apple.dock mineffect -string "scale"`  
Minimise animation: `scale` is faster than the default `genie`. `suck` also exists.

**44.** `com.apple.dock enable-spring-load-actions-on-all-items -bool true`  
Drag a file onto a Dock icon and hold to open that app.

**45.** `com.apple.dock show-process-indicators -bool true`  
The dot under a running app's Dock icon.

**46.** `com.apple.dock launchanim -bool false`  
No bouncing icon when an app launches from the Dock.

**47.** `com.apple.dock expose-animation-duration -float 0.1`  
Speed up the Mission Control animation.

**48.** `com.apple.dock mru-spaces -bool false`  
don't rearrange Spaces

**49.** `com.apple.dock showhidden -bool true`  
Dock icons of hidden apps (⌘H) render translucent, so you can see what is hidden.

**50.** `com.apple.dock show-recents -bool false`  
No 'recent applications' section in the Dock.

**51.** `com.apple.dock mouse-over-hilite-stack -bool true`  
Highlight the item you are hovering in a Dock stack's grid view.


## Activity Monitor

**52.** `com.apple.ActivityMonitor OpenMainWindow -bool true`  
Activity Monitor opens its window on launch instead of only the Dock icon.

**53.** `com.apple.ActivityMonitor IconType -int 5`  
CPU usage in the Dock icon

**54.** `com.apple.ActivityMonitor ShowCategory -int 0`  
all processes

**55.** `com.apple.ActivityMonitor SortColumn -string "CPUUsage"`  
Sort by CPU usage.

**56.** `com.apple.ActivityMonitor SortDirection -int 0`  
Descending, so the biggest consumer is at the top.


## Software Update

**57.** `com.apple.SoftwareUpdate AutomaticCheckEnabled -bool true`  
Check for macOS updates automatically.

**58.** `com.apple.SoftwareUpdate ScheduleFrequency -int 1`  
daily

**59.** `com.apple.SoftwareUpdate AutomaticDownload -int 1`  
Download available updates in the background.

**60.** `com.apple.SoftwareUpdate CriticalUpdateInstall -int 1`  
security updates


## TextEdit

**61.** `com.apple.TextEdit RichText -int 0`  
plain text by default

**62.** `com.apple.TextEdit PlainTextEncoding -int 4`  
UTF-8

**63.** `com.apple.TextEdit PlainTextEncodingForWrite -int 4`  
Save as UTF-8 too, not just read it.


## Terminals

**64.** `com.apple.Terminal StringEncodings -array 4`  
UTF-8 only

**65.** `com.apple.Terminal ShowLineMarks -int 0`  
Turn off the line marks in the Terminal.app scrollback margin.

**66.** `com.apple.Terminal SecureKeyboardEntry -bool true`  
Terminal.app blocks other apps from reading your keystrokes. Note: this can break password-manager autofill into Terminal.

**67.** `com.googlecode.iterm2 PromptOnQuit -bool false`  
iTerm quits without asking for confirmation.


## Misc

**68.** `com.apple.ImageCapture disableHotPlug -bool true`  
Photos doesn't auto-open


## Restart the affected apps


---

**68 settings.**

