from __future__ import annotations

import math
from pathlib import Path

from pycs import CN
from tests.data.base_cfg import schema
from tests.data.base_class import BaseClass

cfg = CN(schema)
cfg.NEW.bool = True
cfg.NEW.int = 1
cfg.NEW.str = "foo"
cfg.NEW.float = math.pi
cfg.NEW.path = Path("example")
cfg.NEW.type = BaseClass
