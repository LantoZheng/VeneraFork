import subprocess
import sys
import shutil
import re
import os

if len(sys.argv) < 2:
    raise SystemExit("Usage: python3 debian/build.py <x64|arm64>")

arch = sys.argv[1]
debianContent = ''
desktopContent = ''
version = ''
flutterVersion = ''

with open('debian/debian.yaml', 'r') as f:
    debianContent = f.read()
with open('debian/gui/venera.desktop', 'r') as f:
    desktopContent = f.read()
with open('pubspec.yaml', 'r') as f:
    version = str.split(str.split(f.read(), 'version: ')[1], '+')[0]
with open('pubspec.yaml', 'r') as f:
    pubspec = f.read()
    match = re.search(r'^\s*flutter:\s*([0-9.]+)\s*$', pubspec, re.MULTILINE)
    if match:
        flutterVersion = match.group(1)

if shutil.which("flutter") is None:
    hint = f"Flutter SDK not found in PATH. Install Flutter {flutterVersion} and retry." if flutterVersion else "Flutter SDK not found in PATH. Install Flutter and retry."
    raise SystemExit(hint)

with open('debian/debian.yaml', 'w') as f:
    content = debianContent.replace('{{Version}}', version)
    if arch == 'x64':
        content = content.replace('{{Arch}}', 'x64')
        content = content.replace('{{Architecture}}', 'amd64')
    elif arch == 'arm64':
        content = content.replace('{{Arch}}', 'arm64')
        content = content.replace('{{Architecture}}', 'arm64')
    f.write(content)
with open('debian/gui/venera.desktop', 'w') as f:
    f.write(desktopContent.replace('{{Version}}', version))

flutterToDebian = shutil.which("flutter_to_debian")
if flutterToDebian is None:
    defaultPath = os.path.join(os.path.expanduser("~"), ".pub-cache", "bin", "flutter_to_debian")
    if os.path.exists(defaultPath) and os.access(defaultPath, os.X_OK):
        flutterToDebian = defaultPath

subprocess.run(["flutter", "build", "linux"], check=True)

if flutterToDebian:
    subprocess.run([flutterToDebian], check=True)
else:
    raise SystemExit("flutter_to_debian not found. Run: dart pub global activate -s git https://github.com/venera-app/flutter_to_debian.git")

with open('debian/debian.yaml', 'w') as f:
    f.write(debianContent)
with open('debian/gui/venera.desktop', 'w') as f:
    f.write(desktopContent)
