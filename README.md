# isomorphism-code

# Installation

Create a python virtual environment and install dependencies

```console
uv venv .venv-iso
source .venv-iso/bin/activate
uv pip install -r requirements.txt --no-cache
```

# Example

To run the tool, simply call `main.py` and it will show you the options

```console
python3 main.py
```

## 1. Pairwise conflicts and across instances

The following call will test for pairwise conflicts between states in Gripper instances

```console
./main.py wl --data-path data/gripper
```
