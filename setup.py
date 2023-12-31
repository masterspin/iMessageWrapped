from setuptools import setup

APP = ['gui.py']
OPTIONS = {
    'argv_emulation': False,
    'packages': ['certifi'],
    'plist': {
        'CFBundleIdentifier': 'com.ritij.imessagewrapped',  # Replace with your app's bundle ID
        'CFBundleName': 'iMessageWrapped',  # Replace with your app's name
        'CFBundleShortVersionString': '1.0',  # Replace with your app's version
        'CSResourcesFileMapped': True,
        'NSAppleEventsUsageDescription': 'Explanation of AppleEvents usage',
        'NSCameraUsageDescription': 'Explanation for camera usage',  # Add other required descriptions
        'NSMicrophoneUsageDescription': 'Explanation for microphone usage',  # Add other required descriptions
        'NSRemindersUsageDescription': 'Explanation for reminders usage',  # Add other required descriptions
        'NSCalendarsUsageDescription': 'Explanation for calendars usage',  # Add other required descriptions
        'Entitlements': './MyApp.entitlements',  # Path to your entitlements file
    }
}

setup(
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
