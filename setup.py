from setuptools import setup

APP = ['main.py']  # Your main Python script
DATA_FILES = []  # Add any additional files if needed
OPTIONS = {
    'argv_emulation': False,
    'packages': ['rumps', 'requests', 'pyperclip', 'openai'],
    'iconfile': 'toolbox.png',
    'plist': {
        'CFBundleName': 'Mac Menubar App',
        'CFBundleDisplayName': 'Mac Menubar App',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleIdentifier': 'com.example.macmenubarapp',
        'LSUIElement': True  # This makes the app a menubar app (no dock icon)
    },
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    install_requires=[
        'pyperclip',
        'openai',
    ],
)
