import rumps
import requests
import os
import subprocess
import threading

APP_NAME = "Menu App"
APP_VERSION = "1.1.93"
GITHUB_API_URL = "https://api.github.com/repos/hamza14102/mac_menubar_app/releases/latest"

class MenubarApp(rumps.App):
    def __init__(self):
        super().__init__("", icon="toolbox.png")
        self.menu = [
            "About",
            "Check for Updates",
            None,
            "Quit"
        ]
        self.quit_button = None

    @rumps.clicked("About")
    def about(self, _):
        rumps.alert(f"{APP_NAME}\nVersion: {APP_VERSION}\nA simple Mac Menubar App.")

    
    def is_version_newer(self, version1, version2):
        version1 = version1.split(".")
        version2 = version2.split(".")
        for i in range(min(len(version1), len(version2))):
            if int(version1[i]) > int(version2[i]):
                return True
            elif int(version1[i]) < int(version2[i]):
                return False
        return len(version1) > len(version2)

    @rumps.clicked("Check for Updates")
    def check_for_updates(self, _):
        rumps.notification(APP_NAME, "Checking for Updates...", "")
        try:
            response = requests.get(GITHUB_API_URL)
            response.raise_for_status()
            data = response.json()

            latest_version = data["tag_name"]
            if self.is_version_newer(latest_version, APP_VERSION):
                download_url = data["assets"][0]["browser_download_url"]
                rumps.notification(APP_NAME, "Update Available!", f"Version {latest_version} is available.")
                # prompt user to download and install the update
                wants_update = rumps.alert("Update Available", f"Version {latest_version} is available. Do you want to download and install?", "Yes", "No") == 1
                if wants_update:
                    # wait for input alert window to close
                    # disable the quit button and the check for updates button
                    self.menu["Check for Updates"].set_callback(None)
                    threading.Thread(target=self.download_and_install_update, args=(download_url,), daemon=True).start()
            else:
                rumps.notification(APP_NAME, "No Updates", "You are using the latest version.")
        except Exception as e:
            rumps.alert("Error", f"Failed to check for updates: {e}")

    def download_and_install_update(self, download_url):
        update_file = "update.dmg"
        try:
            response = requests.get(download_url, stream=True)
            with open(update_file, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            rumps.notification(APP_NAME, "Update Downloaded", "Launching the installer...")
            subprocess.run(["open", update_file])
            # quit the app
            rumps.quit_application()
        except Exception as e:
            rumps.alert("Error", f"Failed to download or install update: {e}")

    @rumps.clicked("Quit", key="q")
    def quit_app(self, _):
        rumps.quit_application()

if __name__ == "__main__":
    MenubarApp().run()
