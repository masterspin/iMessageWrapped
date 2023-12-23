from setuptools import setup

APP = ['gui.py']
DATA_FILES = ['chat.db', 'AddressBook-v22.abcddb']
DATA_FILES = []
OPTIONS = {'argv_emulation': False}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)