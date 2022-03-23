import PyInstaller.__main__

PyInstaller.__main__.run([
    './hand_detection.py',
    '--name=Camera de Segurança',
    # '--noconsole',
    '--noconfirm',
    '--specpath=dist'
])
