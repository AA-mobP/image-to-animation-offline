# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

a = Analysis(
    ['cli.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('data/images/drawing-hand.png', 'data/images'),
        ('data/images/hand-mask.png', 'data/images'),
    ],
    hiddenimports=[
        'cv2',
        'numpy',
        'PIL',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'kivy',
        'kivymd',
        'kivy.app',
        'kivy.uix',
        'kivy.core',
        'kivy.graphics',
        'kivy.lang',
        'kivy.properties',
        'kivy.clock',
        '_tkinter',
        'tkinter',
        'matplotlib',
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Img2Sketch-CLI',
    icon=None,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # CLI needs console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
