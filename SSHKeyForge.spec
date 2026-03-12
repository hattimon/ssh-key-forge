# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

from PyInstaller.utils.hooks import collect_all

# Collect full paramiko + crypto stack
paramiko_datas, paramiko_binaries, paramiko_hidden = collect_all('paramiko')
cryptography_datas, cryptography_binaries, cryptography_hidden = collect_all('cryptography')
bcrypt_datas, bcrypt_binaries, bcrypt_hidden = collect_all('bcrypt')
nacl_datas, nacl_binaries, nacl_hidden = collect_all('nacl')

hiddenimports = []
hiddenimports += paramiko_hidden + cryptography_hidden + bcrypt_hidden + nacl_hidden

# Add extra hidden imports sometimes missed on Windows
hiddenimports += [
    'paramiko.transport',
    'paramiko.auth_handler',
    'paramiko.ssh_exception',
]

datas = []
datas += paramiko_datas + cryptography_datas + bcrypt_datas + nacl_datas
# Bundle bg.mp3
from PyInstaller.utils.hooks import collect_data_files
bg_datas = [('bg.mp3', '.')]

binaries = []
binaries += paramiko_binaries + cryptography_binaries + bcrypt_binaries + nacl_binaries


from PyInstaller.utils.hooks import collect_submodules
hiddenimports += collect_submodules('paramiko')


a = Analysis(
    ['ssh_key_forge.py'],
    pathex=[],
    binaries=binaries,
    datas=datas + bg_datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
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
    name='SSHKeyForge',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='icon.ico',
)
