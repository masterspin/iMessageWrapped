from setuptools import setup

APP = ['gui.py']
OPTIONS = {
    'argv_emulation': False,
    'plist': {
        'CFBundleShortVersionString': '1.0',
        'LSUIElement': True,
        'com.apple.security.filesystem.full-disk-access': True,
        # Add any other entitlements you need
    }
}

setup(
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
