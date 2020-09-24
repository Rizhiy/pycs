# NeuroTrade Config
[![pipeline status](http://192.168.135.11/utilities/config/badges/master/pipeline.svg)](http://192.168.135.11/utilities/config/commits/master)
[![coverage report](http://192.168.135.11/utilities/config/badges/master/coverage.svg)](http://192.168.135.11/utilities/config/commits/master)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Description

Library to define configs for model run.

### Usage

1) Define first-level base config. It can represent a global base config shared between projects.

```python
# global_base_cfg.py
from ntc import CL, CN

class BaseClass:
    pass

cfg = CN()  # Basic config node
cfg.DICT = CN()  # Nested config node
cfg.DICT.FOO = "FOO"  # Config leaf with actual value
cfg.DICT.INT = 1
cfg.NAME = CL(None, str, required=True)  # Specification of config leaf to be defined in children configs
cfg.CLASSES = CN(BaseClass)  # Config node with type specification of its config leafs
cfg.SUBCLASSES = CN(CL(None, BaseClass, subclass=True))  # Config node with subclass specification of its config leafs

def transform(cfg: CN) -> None:
    cfg.DICT.FOO = "BAR"

def validate(cfg: CN) -> None:
    assert len(cfg.NAME) > 0

def hook(cfg: CN) -> None:
    print("Loaded")


# Add transform, validation & hooks function
# Transforms are run after config is loaded and can change values in config
cfg.add_transform(transform)
# Validators are run after transforms and freeze, with them you can verify additional restrictions
cfg.add_validator(validate)
# Hooks are run after validators and can perform additional actions outside of config
cfg.add_hook(hook)
# Validators and hooks should not (and mostly cannot) modify the config
```

2) Define second-level base config, inherited from the first-level one.
It should represent all variables that are changed between experiments inside the project.
It's allowed to add new config nodes to the overall config schema here. 

```python
# project_base_cfg.py
from global_base_cfg import cfg

# Use clone() to inherit from the first-level config.
cfg = cfg.clone()

# Schema changes are allowed here.
cfg.DICT.BAR = "baz"
```

3) Set actual values for each leaf in the config
```python
# my_cfg.py
from ntc import CN

from .project_base_cfg import cfg

# Pass final schema as an argument to the CN() to inherit from the second-level config.
cfg = CN(cfg)

# Schema changes are not allowed here, only leafs can be altered.
cfg.NAME = "Hello World!"
cfg.DICT.INT = 2
```

4) Load actual config and use it in the code. 
```python
# main.py
from ntc import CN

cfg = CN.load("my_cfg.py")
# Config cannot be altered after it is loaded.
assert cfg.NAME == "Hello World!"
assert cfg.DICT.FOO == "BAR"
```


## Installation
Recommended installation with pip:
```bash
pip install ntc
```

## Development
### Formatting
This repository follows strict formatting style which will be checked by the CI.

To properly format the code use **nt-code-style** package:
```bash
pip install nt-code-style
format
```
### Testing
Before uploading a commit you can run `check` which will try to format the files and run tests.
