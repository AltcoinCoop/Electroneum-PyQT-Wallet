# -*- mode: python -*-

block_cipher = None


a = Analysis(['ETN.Gui.Wallet.v.0.1.2.pyw'],
             pathex=['C:\\Users\\philb\\Desktop\\GUI Wallet'],
             binaries=[('etn.ico', '.')],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='ETN.Gui.Wallet.v.0.1.2',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False , icon='etn.ico')
