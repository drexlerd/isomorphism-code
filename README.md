# weifeiler-lehman-code


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

For example, the following call will generate the equivalence classes for a `Gripper` instance with `3` balls and dumps dot representations of the directed edge labelled state graphs in `outputs/decs` and the respective directed vertex labelled state graphs in `outputs/dvcs`.

```
./main.py exact --domain_file_path data/gripper/domain.pddl --problem_file_path data/gripper/instances/p-3-0.pddl --dump-dot
```
