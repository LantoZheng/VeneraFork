import subprocess
import os
import shutil
import re

with open('pubspec.yaml', 'r') as file:
    content = file.read()

flutterVersion = ''
match = re.search(r'^\s*flutter:\s*([0-9.]+)\s*$', content, re.MULTILINE)
if match:
    flutterVersion = match.group(1)

if shutil.which("flutter") is None:
    hint = f"Flutter SDK not found in PATH. Install Flutter {flutterVersion} and retry." if flutterVersion else "Flutter SDK not found in PATH. Install Flutter and retry."
    raise SystemExit(hint)

try:
    import httpx
except ModuleNotFoundError:
    raise SystemExit("Missing dependency: httpx. Run: pip install httpx")

subprocess.run(["flutter", "build", "windows"], check=True)

if os.path.exists("build/app-windows.zip"):
    os.remove("build/app-windows.zip")

version = str.split(str.split(content, 'version: ')[1], '+')[0]

subprocess.run([
    "tar",
    "-a",
    "-c",
    "-f",
    f"build/windows/Venera-{version}-windows.zip",
    "-C",
    "build/windows/x64/runner/Release",
    "*",
], check=True)

issContent = ""
file = open('windows/build.iss', 'r')
issContent = file.read()
newContent = issContent
newContent = newContent.replace("{{version}}", version)
newContent = newContent.replace("{{root_path}}", os.getcwd())
file.close()
file = open('windows/build.iss', 'w')
file.write(newContent)
file.close()

if not os.path.exists("windows/ChineseSimplified.isl"):
    # download ChineseSimplified.isl
    url = "https://cdn.jsdelivr.net/gh/kira-96/Inno-Setup-Chinese-Simplified-Translation@latest/ChineseSimplified.isl"
    response = httpx.get(url)
    with open('windows/ChineseSimplified.isl', 'wb') as file:
        file.write(response.content)

subprocess.run(["iscc", "windows/build.iss"], check=True)

with open('windows/build.iss', 'w') as file:
    file.write(issContent)
