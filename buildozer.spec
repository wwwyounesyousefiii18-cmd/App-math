[app]
# (str) Title of your application
 title = Math Tools
# (str) Package name
 package.name = mathtools
# (str) Package domain (needed for android package name)
 package.domain = org.example
# (str) Source code where main.py lives
 source.dir = .
# (str) Main entry point
 source.main = main.py
# (str) Application version
 version = 1.0
# (list) Application requirements
 requirements = python3,kivy
# (str) Supported orientation (portrait, landscape, all)
 orientation = portrait
# (bool) fullscreen
 fullscreen = 0
# (str) Icon
# icon.filename = %(source.dir)s/icon.png
# (list) List of service to start with the application
# services = NAME:ENTRYPOINT_TO_PY,NAME2:ENTRYPOINT2_TO_PY

[buildozer]
# (int) Log level (0 = error only, 1 = info, 2 = debug)
 log_level = 2
# (int) Warning this is only for the first build; leave empty for CI caching
 warn_on_root = 1

[app:android]
# (str) Android app title
 android.entrypoint = org.kivy.android.PythonActivity
# (int) Minimum API level supported
 android.minapi = 23
# (int) Target API level
 android.api = 35
# (str) Android NDK version
 android.ndk = 27c
# (bool) AndroidX support
 android.enable_androidx = 1
# (str) Android archs
 android.archs = arm64-v8a, armeabi-v7a
# (bool) Copy python files into the APK
# android.add_src =

[buildozer:android]
# Kept for compatibility with Buildozer versions that use this section.
