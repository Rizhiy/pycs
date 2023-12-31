from __future__ import annotations

from pycs import CN

from ..base_cfg import cfg


def hook(cfg: CN) -> None:
    print(cfg.NAME)


cfg = cfg.inherit()

cfg.add_hook(hook)
