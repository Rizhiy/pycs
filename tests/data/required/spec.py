from __future__ import annotations

from pycs import CN
from tests.data.base_class import BaseClass
from tests.data.required.required_spec import schema

cfg = CN(schema)
cfg.REQUIRED_CLASSES.ONE = BaseClass()
