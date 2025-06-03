import ollama
import subprocess
import time
import os
import signal
from langchain_ollama import OllamaLLM

ollama_serve_process = None


def get_llm(model_name, config=None):
    model_config = config.get("model_config", {}).get("ollama", {}).get(model_name, {})
    model_id = model_config.get("model_identifier")
    llm = OllamaLLM(model=model_id)
    return llm


def load_model(model_name, config=None):
    model_config = config.get("model_config", {}).get("ollama", {}).get(model_name, {})
    model_id = model_config.get("model_identifier")

    def ollama_generate(prompt, **kwargs):
        response = ollama.chat(
            model=model_id, messages=[{"role": "user", "content": prompt}]
        )
        return response["message"]["content"]

    print(f"[Ollama Loader] Ready to use model: {model_name}")
    return ollama_generate


def download_ollama_model(model_name: str) -> bool:
    """
    Downloads the given Ollama model by running 'ollama pull <model_name>' in a subprocess.

    Args:
        model_name (str): The Ollama model name to download.

    Returns:
        bool: True if download succeeded, False otherwise.
    """
    try:
        # Run the ollama pull command
        result = subprocess.run(
            ["ollama", "pull", model_name],
            capture_output=True,
            text=True,
            check=True,  # raises CalledProcessError on non-zero exit
        )
        print(f"Successfully downloaded model '{model_name}'. Output:\n{result.stdout}")
        return True

    except subprocess.CalledProcessError as e:
        print(f"Failed to download model '{model_name}'. Error:\n{e.stderr}")
        return False
    except FileNotFoundError:
        print(
            "Ollama CLI not found. Please make sure Ollama is installed and 'ollama' is in your PATH."
        )
        return False


def start_ollama_app():
    try:
        subprocess.Popen(["open", "-a", "Ollama"])
        print("Ollama app started.")
    except Exception as e:
        print(f"Failed to start Ollama app: {e}")


def is_ollama_running():
    try:
        output = subprocess.check_output(["pgrep", "-f", "Ollama"])
        return bool(output.strip())
    except subprocess.CalledProcessError:
        return False


def is_model_downloaded(model_name):
    try:
        result = subprocess.run(
            ["ollama", "list"], capture_output=True, text=True, check=True
        )
        # Check if model name appears in the output list
        return model_name in result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error listing Ollama models:\n{e.stderr}")
        return False


def start_ollama_daemon():
    global ollama_serve_process
    if ollama_serve_process is None or ollama_serve_process.poll() is not None:
        # Start ollama serve in background
        ollama_serve_process = subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid,  # for clean kill later
        )
        print("Started Ollama daemon with 'ollama serve'.")


def stop_ollama_daemon():
    global ollama_serve_process
    if ollama_serve_process is not None:
        os.killpg(os.getpgid(ollama_serve_process.pid), signal.SIGTERM)
        print("Stopped Ollama daemon.")
        ollama_serve_process = None


def is_ollama_daemon_ready(retries=10, delay=2):
    for i in range(retries):
        try:
            subprocess.run(["ollama", "list"], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            print(f"Waiting for Ollama daemon... retry {i + 1}/{retries}")
            time.sleep(delay)
    return False


def make_model_available(model_name, config=None):
    # Start daemon if not running
    start_ollama_daemon()

    if not is_ollama_daemon_ready():
        raise RuntimeError("Ollama daemon not ready after retries.")

    # Check if model downloaded, else download it
    if not is_model_downloaded(model_name):
        download_ollama_model(model_name)
    else:
        print(f"Model '{model_name}' already downloaded.")

    # Load the model using your runner
    llm = load_model(model_name, config=config or {})
    print(f"Model '{model_name}' ready to use.")
    return llm
