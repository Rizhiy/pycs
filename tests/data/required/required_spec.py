from __future__ import annotations

from pycs import CL, CN

from ..base_cfg import schema
from ..base_class import BaseClass

schema = schema.inherit()
schema.REQUIRED_CLASSES = CN(CL(None, BaseClass, required=True))
