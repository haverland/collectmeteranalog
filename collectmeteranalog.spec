# -*- mode: python ; coding: utf-8 -*-

import os
import sys

# Windows OS: Populate versioninfo structure
if sys.platform == "win32":
    # Load version from source file
    version_source = {}
    with open(os.path.join("collectmeteranalog", "__version__.py")) as f:
        exec(f.read(), version_source)
    
    __version__ = version_source["__version__"]

    from PyInstaller.utils.win32.versioninfo import FixedFileInfo, VSVersionInfo, StringFileInfo, StringTable, StringStruct

    def make_fixed_file_info(version_str):
        parts = list(map(int, version_str.split(".")))
        while len(parts) < 4:
            parts.append(0)
        return FixedFileInfo(
            filevers=tuple(parts),
            prodvers=tuple(parts),
            mask=0x3F,
            flags=0x0,
            OS=0x40004,
            fileType=0x1,
            subtype=0x0,
            date=(0, 0)
        )

    # Create versioninfo structure
    ffi = make_fixed_file_info(__version__)

    version_file = VSVersionInfo(
        ffi=ffi,
        kids=[
            StringFileInfo([
                StringTable(
                    '040904B0',
                    [
                        StringStruct('CompanyName', ''),
                        StringStruct('FileDescription', 'Analog Meter Collector'),
                        StringStruct('FileVersion', __version__),
                        StringStruct('InternalName', 'collectmeteranalog'),
                        StringStruct('OriginalFilename', 'collectmeteranalog.exe'),
                        StringStruct('ProductName', 'CollectMeterAnalog'),
                        StringStruct('ProductVersion', __version__),
                    ]
                )
            ])
        ]
    )
else: # Skip for non-Windows OS
    version_file = None


block_cipher = None


a = Analysis(
    ['run.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=['requests'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='collectmeteranalog',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version=version_file,
)
