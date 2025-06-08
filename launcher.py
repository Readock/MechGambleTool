import os
import re
import sys

import requests
import zipfile
import shutil
import subprocess
import tempfile
from pathlib import Path
from packaging.version import Version, InvalidVersion
from PyQt5.QtWidgets import QApplication, QMessageBox

VERSION_FOLDER_PATTERN = re.compile(r"v(\d.+)")


def get_latest_local_version():
    version_dirs = []
    for entry in Path(".").iterdir():
        if entry.is_dir():
            match = VERSION_FOLDER_PATTERN.fullmatch(entry.name)
            if match:
                try:
                    version_dirs.append((Version(match.group(1)), entry))
                except InvalidVersion:
                    continue
    if not version_dirs:
        return None, None
    version_dirs.sort(reverse=True)
    return version_dirs[0]  # (Version, Path)


def get_latest_release_info():
    url = f"https://github.com/Readock/MechGambleTool/releases/latest"
    response = requests.get(url, allow_redirects=False)
    response.raise_for_status()
    version_str = response.headers.get("location").rsplit("/", 1)[1].lstrip("v")
    zip_url = f"https://github.com/Readock/MechGambleTool/releases/download/v{version_str}/MechGambleTool.zip"
    return Version(version_str), zip_url


def download_and_extract_zip(zip_url, version_obj):
    response = requests.get(zip_url, stream=True)
    response.raise_for_status()
    zip_path = tempfile.mktemp(suffix=".zip")
    print(f"Creating temp file: {zip_path}")
    with open(zip_path, "wb") as f:
        f.write(response.content)

    folder_name = f"v{version_obj}"
    version_dir = Path(folder_name)
    print(f"Creating new version: {version_dir}")
    if version_dir.exists():
        shutil.rmtree(version_dir)
    version_dir.mkdir(parents=True)

    print(f"Extracting zip contents into: {version_dir}")
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(version_dir)

    print(f"Removing temp file: {zip_path}")
    os.remove(zip_path)
    return version_dir


def find_exe_in_folder(folder: Path):
    for file in folder.iterdir():
        if file.name == "MechGambleTool.exe" and file.is_file():
            return file
    raise FileNotFoundError(f"No MechGambleTool.exe found in {folder}")


def launch_exe(exe_path: Path):
    print(f"Launching {exe_path}")
    subprocess.Popen([str(exe_path)])



#def ask_should_update(current, next, url):
#    app = QApplication.instance() or QApplication(sys.argv)
#    root.withdraw()
#    return messagebox.askyesno("Update available!", f"""Current Version: {current}
#New Version: {next}
#
#{url}
#
#Do you want to download and install the new version?
#    """)


def ask_should_update(current, next, url):
    # Create QApplication if none exists
    app = QApplication.instance() or QApplication(sys.argv)

    # Create and configure the message box
    msg_box = QMessageBox()
    msg_box.setWindowTitle("Update available!")
    msg_box.setText(f"Current Version: {current}\nNew Version: {next}\n\n{url}")
    msg_box.setInformativeText("Do you want to download and install the new version?")
    msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    msg_box.setDefaultButton(QMessageBox.Yes)

    # Execute the dialog and return True for Yes, False for No
    result = msg_box.exec_()
    return result == QMessageBox.Yes

def clean_old_versions(exclude_folder: Path):
    for entry in Path(".").iterdir():
        if entry.is_dir() and entry != exclude_folder and VERSION_FOLDER_PATTERN.match(entry.name):
            shutil.rmtree(entry, ignore_errors=True)


def main():
    local_version, local_folder = get_latest_local_version()
    latest_version, zip_url = get_latest_release_info()
    print(f"Detected Version: {local_version}")
    print(f"Latest Version: {latest_version}")

    needs_update = local_version is None or latest_version > local_version

    if not needs_update or not ask_should_update(local_version, latest_version, zip_url):
        if local_folder:
            exe_path = find_exe_in_folder(local_folder)
            launch_exe(exe_path)
        return

    print(f"Downloading v{latest_version} version from: {zip_url}")
    new_folder = download_and_extract_zip(zip_url, latest_version)
    exe_path = find_exe_in_folder(new_folder)
    print(f"Downloaded successfully!")

    print(f"Deleting current resource folder...")
    shutil.rmtree("resources", ignore_errors=True)
    print(f"Copy new resource folder...")
    shutil.copytree(new_folder / "resources", "resources", dirs_exist_ok=True)

    launch_exe(exe_path)

    print(f"Deleting old versions...")
    clean_old_versions(Path(f"v{latest_version}"))


if __name__ == "__main__":
    print("""
  __  __  _____ _______            _                            _               
 |  \/  |/ ____|__   __|          | |                          | |              
 | \  / | |  __   | |     ______  | |     __ _ _   _ _ __   ___| |__   ___ _ __ 
 | |\/| | | |_ |  | |    |______| | |    / _` | | | | '_ \ / __| '_ \ / _ \ '__|
 | |  | | |__| |  | |             | |___| (_| | |_| | | | | (__| | | |  __/ |   
 |_|  |_|\_____|  |_|             |______\__,_|\__,_|_| |_|\___|_| |_|\___|_|   
========================== MechGabmleTool - Launcher ===========================
    """)
    main()
    sys.exit(0)
