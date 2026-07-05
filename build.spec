# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller spec for Agency Image Pipeline.
#
# This bundles main.py + the entire app/ package into a SINGLE
# standalone Windows .exe with NO console window (windowed=True),
# so the end user just double-clicks it — no Python, no terminal,
# no installation required on their machine.
#
# Build with:  pyinstaller build.spec        (see build.bat for a
# one-click version that also creates/activates the venv for you)

import sys
from pathlib import Path

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),   # bundle icons/logo into the exe
    ],
    hiddenimports=[
        'customtkinter',
        'PIL._tkinter_finder',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AgencyImagePipeline',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # <-- windowed app, no black terminal window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icons/app_icon.ico',
)
