# isomorphism-code

# Installation

Create a python virtual environment and install dependencies

```console
python3 -m venv --prompt wl .venv
source .venv/bin/activate
pip install -r requirements.txt
```

# Example

To run the tool, simply call `main.py` and it will show you the options

```console
python3 main.py
```

## 1. Pairwise conflicts and across instances

The following call will test for pairwise conflicts between states in Gripper instances

```console
./main.py pairwise-wl --data-path data/gripper
```


## 2. Pairwise conflicts on single instance

The following call will test for pairwise conflicts between states in Gripper instances

```console
./main.py wl --domain_file_path data/gripper/domain.pddl --problem_file_path data/gripper/p-1-0.pddl
```