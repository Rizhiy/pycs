from ntc import CN

from .base_cfg import cfg as bc


def transform(cfg: CN) -> None:
    if cfg.DICT.FOO == "foo":
        cfg.DICT.FOO = "bar"


cfg = CN(bc, transformers=[transform])
cfg.NAME = "Name"