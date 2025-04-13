# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['fully_integrated.py'],  # Tên file Python của launcher tích hợp
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'PIL', 
        'PIL._imagingtk', 
        'PIL._tkinter_finder', 
        'tkinter', 
        'tkinter.filedialog', 
        'tkinter.messagebox',
        'tkinter.ttk',
        'tkinter.simpledialog',
        'requests',
        'io',
        'io.BytesIO',
        'threading',
        'subprocess',
        'tempfile',
        'shutil',
        'getpass',
        'json'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Thêm file công cụ để nhúng vào bên trong EXE
a.datas += [('calculator.py', 'SVS_Utility_Tool.py', 'DATA')]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SVS_Utility_Tool',  # Tên file .exe đầu ra
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Đặt thành True nếu muốn debug với console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
