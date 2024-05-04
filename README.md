# smp

Command-line music player written in Python.

## Quick Start

```sh
cd ./smp
python -m venv .venv
source ./.venv/bin/activate
python -m pip install -r requirements.txt
```

## With pyenv
Alternatively, you could do this with `pyenv-virtualenv`:
```sh
cd ./smp
pyenv virtualenv smp  # with Python 3.8 or newer
pyenv activate smp
python -m pip install -r requirements.txt
```
Optional:
```sh
chmod +x smp
echo smp > .python-version  # Automatically activate the environment
```

## Help
smp has an interactive help session that can be accessed by typing
`help` while in smp. From here you can get a list of
commands and detailed explanations.

