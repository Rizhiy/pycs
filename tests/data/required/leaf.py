from __future__ import annotations

from ntc import CN
from tests.data.required.required_leaf import cfg

cfg = CN(cfg)
cfg.REQUIRED = "Required"
