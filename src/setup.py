import subprocess
import sys
from pathlib import Path
import os

PROJECT_ROOT = Path(__file__).resolve().parent.parent
VENV_DIR = PROJECT_ROOT / ".venv"
# print(PROJECT_ROOT)
LLM_BRAIN = "qwen2.5:3b"

steps = 1

def get_venv_python() -> Path:
    """Returns the OS-specific path to the Python executable inside .venv."""
    if os.name == "nt":  # Windows
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"  # Linux / macOS / WSL

def run_command(commands : list[str], description: str):
    """Runs all setup commands"""
    global steps
    print(f"Step {steps}: {description}")
    print(f"Command Running: {"".join(commands)}")
    choice = input("You wish to coninue? : (Y/N)")
    if(choice.lower() == 'y' or choice.lower() == 'yes'):
        try : 
            subprocess.run(commands, cwd=PROJECT_ROOT, check=True)
        except FileNotFoundError:
            print(f"\n[ERROR] Command not found: '{commands[0]}'. Make sure it is installed and in your PATH.")
            sys.exit(1)
        except subprocess.CalledProcessError as e:
            print(f"\n[ERROR] Step failed with exit code {e.returncode}. Aborting setup.")
            sys.exit(e.returncode)
    else:
        print("Moving on to the next step...")
    steps+=1

def main():

    if not VENV_DIR.exists():
        run_command(
            [sys.executable,"-m","venv",str(VENV_DIR)],
            description="Setting up an Virtual Environment"
        )
    else:
        print("Virtual Environment already exists.")

    venv_python = get_venv_python()
    
    run_command(
        [str(venv_python),'-m','pip','install','-r','requirements.txt'],
        description="Installing python requirements to .venv"
    )

    run_command(
            [str(venv_python),'-m','pip','install','-r','requirements.txt'],
            description="Installing python requirements to .venv"
    )

    run_command(
            ["ollama","create","vashistAI","-f","Modelfile"],
            description="Building custom Ollama Model"
    )

    run_command(
                ["ollama","pull","nomic-embed-text"],
                description="Installing Embedding Model"
    )
    run_command(
                ["ollama","pull",f"{LLM_BRAIN}"],
                description="Installing LLM Model"
    )

if __name__=="__main__":
    main()

