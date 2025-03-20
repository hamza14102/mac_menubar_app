import subprocess
import time
import requests
import shutil

class OllamaGemmaWrapper:
    def __init__(self, model="gemma3", server_url="http://localhost:11434"):
        """
        Initialize the wrapper with the specified model and server URL.
        Ensures that Ollama is installed and that the server is running.
        """
        self.check_ollama_installed()
        self.model = model
        self.server_url = server_url
        self.api_chat_endpoint = f"{self.server_url}/api/chat"
        self.server_process = None
        self.ensure_server_running()

    def check_ollama_installed(self):
        """
        Checks if the Ollama command is available in the system.
        Raises an error with instructions if it's not found.
        """
        if shutil.which("ollama") is None:
            raise EnvironmentError(
                "Ollama is not installed or not found in PATH. "
                "Please install Ollama from https://ollama.com/download"
            )

    def is_server_running(self):
        """
        Check if the Ollama server is up by sending a simple GET request.
        Returns True if it responds, otherwise False.
        """
        try:
            res = requests.get(self.server_url, timeout=1)
            return res.status_code == 200
        except Exception:
            return False

    def ensure_server_running(self):
        """
        Ensure that the Ollama server is running. If not, start it as a subprocess.
        Wait for the server to become responsive before returning.
        """
        if not self.is_server_running():
            print("Ollama server is not running, launching it as a subprocess...")
            self.server_process = subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            # Wait until the server is up (with a timeout)
            timeout = 10  # seconds
            start_time = time.time()
            while time.time() - start_time < timeout:
                if self.is_server_running():
                    print("Ollama server is now running.")
                    return
                time.sleep(0.5)
            print("Warning: Ollama server did not start in time.")
        else:
            print("Ollama server is already running.")

    def ask(self, prompt):
        """
        Send a prompt to the Gemma 3 model via the Ollama chat API and return the response.
        The prompt is wrapped in a single message conversation.
        """
        # Build the chat message payload
        messages = [{"role": "user", "content": prompt}]
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }
        try:
            response = requests.post(self.api_chat_endpoint, json=payload, timeout=30)
            response.raise_for_status()
        except Exception as e:
            print("Error querying Ollama API:", e)
            return f"Error: {e}"
        
        data = response.json()
        reply = data.get("message", {}).get("content", "")
        return reply

    def shutdown(self):
        """
        Shutdown the Ollama server process if it was started by this wrapper.
        """
        if self.server_process is not None:
            self.server_process.terminate()
            self.server_process = None

    def get_mail_response(self, mail_content):
        """
        Get the response from Gemma 3 for a given email content.
        """
        
        messages = [
            {"role": "user", "content": "You are an AI assistant designed to generate professional, concise, and relevant email responses. The responses should be tailored based on the tone and content of the original email while maintaining a polite, respectful, and clear style. If the email requires a technical response, you should ensure the reply is precise and accurate. If needed, uou should consider the user's recent professional background, including their work with advanced AI technologies, software development practices, and their specific focus on creating custom neural networks and AI tools. Ensure that the email response follows a polite but efficient tone, reflecting the user's background and current professional endeavors. No need to provide the subject in your response."},
            {"role": "user", "content": mail_content}
        ]
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }
        try:
            response = requests.post(self.api_chat_endpoint, json=payload, timeout=30)
            response.raise_for_status()
        except Exception as e:
            print("Error querying Ollama API:", e)
            return f"Error: {e}"
        
        data = response.json()
        reply = data.get("message", {}).get("content", "")
        return reply

# # Example usage:
# if __name__ == "__main__":
#     try:
#         wrapper = OllamaGemmaWrapper()
#         user_prompt = "Who are you?"
#         print("Sending prompt:", user_prompt)
#         response = wrapper.ask(user_prompt)
#         print("Gemma 3 responded:", response)
#     except EnvironmentError as e:
#         print(e)
#     # finally:
#     #     # Optionally shut down the server if you started it here.
#     #     if 'wrapper' in locals():
#     #         print("Shutting down the Ollama server...")
#     #         wrapper.shutdown()