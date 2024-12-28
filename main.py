import rumps
import requests
import os
import subprocess
import threading
from openai import OpenAI
import pyperclip as pc

APP_NAME = "Menu App"
APP_VERSION = "1.2.4"
GITHUB_API_URL = "https://api.github.com/repos/hamza14102/mac_menubar_app/releases/latest"

def generate_response(email_content):
    try:
        client = OpenAI()
    except Exception as e:
        return f"An error occurred: {str(e)}"
    prompt = f"Write a professional email response to the following:\n\n{email_content}"
    # print(prompt)
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an AI assistant designed to generate professional, concise, and relevant email responses. The responses should be tailored based on the tone and content of the original email while maintaining a polite, respectful, and clear style. If the email requires a technical response, you should ensure the reply is precise and accurate. If needed, uou should consider the user's recent professional background, including their work with advanced AI technologies, software development practices, and their specific focus on creating custom neural networks and AI tools. Ensure that the email response follows a polite but efficient tone, reflecting the user's background and current professional endeavors. No need to provide the subject in your response."},
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    return completion.choices[0].message.content

def select_email_content_and_copy():
    script = '''
    tell application "Mail"
        activate
        tell application "System Events"
            keystroke "a" using {command down}
            delay 0.1
            keystroke "c" using {command down}
            delay 0.1
            keystroke (ASCII character 30) -- Up arrow key to unselect all
        end tell
    end tell
    '''
    subprocess.run(['osascript', '-e', script])

def inject_reply_content(response_content):
    """
    Inject the generated response into the reply draft in Mail.
    """
    pc.copy(response_content)
    script = '''
    tell application "Mail"
        activate
        tell application "System Events"
            keystroke "v" using {command down}
        end tell
    end tell
    '''
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)

class MenubarApp(rumps.App):
    def __init__(self):
        super().__init__("", icon="toolbox.png")
        self.menu = [
            "Reply to Mail",
            None,
            "About",
            "Check for Updates",
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
                    # disable the check for updates button
                    self.menu["Check for Updates"].set_callback(None)
                    # replace the check for updates button title with "Downloading..."
                    self.menu["Check for Updates"].title = "Downloading..."
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


# ======================== Reply to Mail ========================

    @rumps.clicked("Reply to Mail")
    def reply_to_mail(self, _):
        select_email_content_and_copy()
        email_content = pc.paste()
        response_content = generate_response(email_content)
        inject_reply_content(response_content)

if __name__ == "__main__":
    MenubarApp().run()
