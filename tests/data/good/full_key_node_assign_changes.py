from __future__ import annotations

from pycs import CN
from tests.data.good.full_key_node_assign import cfg

cfg = CN(cfg)

cfg.FOO.BAR = "foo"
