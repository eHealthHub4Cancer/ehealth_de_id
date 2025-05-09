from setuptools import setup

APP = ['main.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    'packages': [
        'wx', 
        'numpy', 
        'crypt4gh', 
        'cryptography',
        'openpyxl',
        'bcrypt',
        'nacl',
        'cffi',
    ],
    'includes': [
        'wx.adv',
        'wx.html',
        'base64',
        'datetime',
        'gettext',
        'logging',
        'os',
        'subprocess',
        'sys',
    ],
    'frameworks': ['libcrypto.dylib', 'libssl.dylib'],
    'iconfile': 'ehealth_icon.icns',
    'plist': {
        'CFBundleName': 'E-Health ID Generator',
        'CFBundleDisplayName': 'E-Health ID Generator',
        'CFBundleIdentifier': 'com.ehealth.idgenerator',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHumanReadableCopyright': 'Copyright 2025 @Ehealth Hub',
    }
}

setup(
    name="E-Health ID Generator",
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)