from __future__ import annotations

from collections import UserDict
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple, Union

import yaml

from ntc.errors import MissingRequired, NodeFrozenError, NodeReassignment, SaveError, SchemaError, SchemaFrozenError
from ntc.utils import add_yaml_str_representer, import_module, merge_cfg_module

from .leaf import CfgLeaf


class CfgNode(UserDict):
    _BUILT_IN_ATTRS = (
        "_schema_frozen",
        "_frozen",
        "_was_unfrozen",
        "_leaf_spec",
        "_module",
        "_new_allowed",
        "_transforms",
        "_validators",
        "_hooks",
    )
    RESERVED_KEYS = (*_BUILT_IN_ATTRS, "data")

    def __init__(
        self, first: Any = None, *, schema_frozen: bool = False, frozen: bool = False, new_allowed: bool = False,
    ):
        super().__init__()
        if isinstance(first, (dict, CfgNode)):
            base, leaf_spec = first, None
        else:
            base, leaf_spec = None, first
        if leaf_spec is not None and not isinstance(leaf_spec, CfgLeaf):
            leaf_spec = CfgLeaf(None, leaf_spec)

        self._schema_frozen = schema_frozen
        self._frozen = frozen
        self._new_allowed = new_allowed
        self._was_unfrozen = False
        self._leaf_spec = leaf_spec
        self._validators = []
        self._transforms = []
        self._hooks = []
        self._module = None

        if base is not None:
            self._init_with_base(base)

    def __setitem__(self, key: str, value: Any) -> None:
        if self.frozen:
            raise NodeFrozenError()
        if key in self:
            self._set_existing(key, value)
        else:
            self._set_new(key, value)

    def _get_raw(self, key):
        if key not in self:
            raise KeyError(key)
        return super().__getitem__(key)

    def __getitem__(self, key: str) -> Any:
        attr = self._get_raw(key)
        if isinstance(attr, CfgLeaf):
            return attr.value
        return attr

    def __getattr__(self, key: str) -> Any:
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __setattr__(self, key: str, value: Any) -> None:
        if key in self.RESERVED_KEYS:
            super().__setattr__(key, value)
        else:
            self[key] = value

    def __eq__(self, other: CfgNode) -> bool:
        return self.to_dict() == other.to_dict()

    def __str__(self) -> str:
        add_yaml_str_representer()
        attrs = self.to_dict()
        return yaml.dump(attrs)

    @staticmethod
    def load(cfg_path: Union[Path, str]) -> CfgNode:
        cfg_path = Path(cfg_path)
        module = import_module(cfg_path)
        cfg: CfgNode = module.cfg
        if not cfg.schema_frozen:
            raise SchemaError("Changes to config must be started with `cfg = CN(cfg)`")
        if hasattr(cfg, "NAME"):
            cfg.NAME = cfg.NAME or cfg_path.stem
        cfg.set_module(merge_cfg_module(module))
        cfg.transform()
        cfg.freeze()
        cfg.validate()
        cfg.run_hooks()

        return cfg

    @staticmethod
    def validate_required(cfg: CfgNode) -> None:
        if cfg.leaf_spec is not None and cfg.leaf_spec.required and len(cfg) == 0:
            raise MissingRequired(f"Missing required members for {cfg.leaf_spec}")
        for key, attr in cfg.attrs:
            if isinstance(attr, CfgNode):
                CfgNode.validate_required(attr)
                continue
            if attr.required and attr.value is None:
                raise MissingRequired(f"Key {key} is required, but was not provided.")

    def save(self, path: Path) -> None:
        if self._was_unfrozen:
            raise SaveError("Trying to save config which was unfrozen.")
        if not self._module:
            raise SaveError("Config was not loaded.")
        with path.open("w") as f:
            f.writelines(self._module)

    def clone(self) -> CfgNode:
        cfg = CfgNode(self)
        cfg._leaf_spec = self.leaf_spec
        cfg.unfreeze_schema()
        return cfg

    def transform(self) -> None:
        """
        Specify additional changes to be made after manual changes, run during loading from file
        """
        for transformer in self._transforms:
            transformer(self)

    def validate(self) -> None:
        """
        Check additional rules for config, run during loading after transform
        """
        validators = [CfgNode.validate_required] + self._validators
        for validator in validators:
            validator(self)

    def run_hooks(self) -> None:
        """
        Perform actions based on config, run during loading after validation
        Hooks should NOT modify the config
        """
        for hook in self._hooks:
            hook(self)

    def add_transform(self, transform: Callable[[CfgNode], None]) -> None:
        if self._schema_frozen:
            raise SchemaFrozenError("Can't add transform after schema has been frozen")
        self._transforms.append(transform)

    def add_validator(self, validator: Callable[[CfgNode], None]) -> None:
        if self._schema_frozen:
            raise SchemaFrozenError("Can't add validator after schema has been frozen")
        self._validators.append(validator)

    def add_hook(self, hook: Callable[[CfgNode], None]) -> None:
        if self._schema_frozen:
            raise SchemaFrozenError("Can't add hook after schema has been frozen")
        self._hooks.append(hook)

    def to_dict(self) -> Dict[str, Any]:
        attrs = {}
        for key, attr in self.attrs:
            if isinstance(attr, CfgNode):
                attrs[key] = attr.to_dict()
            else:
                attrs[key] = attr.value
        return attrs

    @property
    def attrs(self) -> List[Tuple[str, Union[CfgNode, CfgLeaf]]]:
        attrs_list = []
        for key in super().keys():
            value = self._get_raw(key)
            if isinstance(value, (CfgNode, CfgLeaf)):
                attrs_list.append((key, value))
        return attrs_list

    def freeze_schema(self) -> None:
        self._schema_frozen = True
        for key, attr in self.attrs:
            if isinstance(attr, CfgNode):
                attr.freeze_schema()

    def unfreeze_schema(self) -> None:
        self._schema_frozen = False
        for key, attr in self.attrs:
            if isinstance(attr, CfgNode):
                attr.unfreeze_schema()

    def freeze(self) -> None:
        self._frozen = True
        for key, attr in self.attrs:
            if isinstance(attr, CfgNode):
                attr.freeze()

    def unfreeze(self) -> None:
        self._frozen = False
        self._was_unfrozen = True
        for key, attr in self.attrs:
            if isinstance(attr, CfgNode):
                attr.unfreeze()

    @property
    def schema_frozen(self) -> bool:
        return self._schema_frozen

    @property
    def frozen(self) -> bool:
        return self._frozen

    @property
    def leaf_spec(self) -> CfgLeaf:
        return self._leaf_spec

    def set_module(self, module) -> None:
        self._module = module

    def _set_attrs(self, attrs: List[Tuple[str, Union[CfgNode, CfgLeaf]]]) -> None:
        for key, attr in attrs:
            setattr(self, key, attr.clone())

    def _set_new(self, key: str, value: Any) -> None:
        leaf_spec = self.leaf_spec
        if isinstance(value, CfgNode):
            if leaf_spec:
                raise SchemaError(f"Key {key} cannot contain nested nodes as leaf spec is defined for it.")
            if self._schema_frozen and not self._new_allowed:
                raise SchemaFrozenError(f"Trying to add node {key}, but schema is frozen.")
            value_to_set = value
        elif isinstance(value, CfgLeaf):
            value_to_set = value
        elif isinstance(value, type):
            if leaf_spec:
                value_to_set = CfgLeaf(
                    value if leaf_spec.subclass else None,
                    value,  # Need to pass value here instead of copying, in case new value is more restrictive
                    subclass=leaf_spec.subclass,
                    required=leaf_spec.required,
                )
            else:
                value_to_set = CfgLeaf(None, value)
        elif leaf_spec:
            value_to_set = leaf_spec.clone()
            value_to_set.value = value
        else:
            value_to_set = CfgLeaf(value, type(value), required=True)

        if isinstance(value_to_set, CfgLeaf):
            if leaf_spec:
                if leaf_spec.required and not value_to_set.required:
                    raise SchemaError(f"Leaf at {key} must have required == True")
                if leaf_spec.subclass != value_to_set.subclass:
                    raise SchemaError(f"Leaf at {key} must have subclass == True")
                if not issubclass(value_to_set.type, leaf_spec.type):
                    raise SchemaError(f"Required type for leaf at {key} must be subclass of {leaf_spec.type}")
                if not leaf_spec.required and value_to_set.value is None:
                    pass
                elif leaf_spec.subclass and not isinstance(value_to_set.value, type):
                    raise SchemaError(f"Leaf value at {key} must be a type")
                elif not leaf_spec.subclass and not isinstance(value_to_set.value, leaf_spec.type):
                    raise SchemaError(f"Value at {key} must be instance of {leaf_spec.type}")
            elif self._schema_frozen and not self._new_allowed:
                raise SchemaFrozenError(f"Trying to add leaf {key} to node with frozen schema, but without leaf spec.")
        super().__setitem__(key, value_to_set)

    def _set_existing(self, key: str, value: Any) -> None:
        cur_attr = super().__getitem__(key)
        type(value)
        if isinstance(cur_attr, CfgNode):
            raise NodeReassignment(f"Nested CfgNode {key} cannot be reassigned.")
        elif isinstance(cur_attr, CfgLeaf):
            cur_attr.value = value
        else:
            raise AssertionError("This should not happen!")

    def _init_with_base(self, base: Union[dict, CfgNode]) -> None:
        if isinstance(base, CfgNode):
            self._transforms = base._transforms + self._transforms
            self._validators = base._validators + self._validators
            self._hooks = base._hooks + self._hooks
            self._set_attrs(base.attrs)
            self.freeze_schema()
        elif isinstance(base, dict):
            for key, value in base.items():
                if isinstance(value, dict):
                    value = CfgNode(value)
                self[key] = value
        else:
            raise ValueError("This should not happen!")


CN = CfgNode

__all__ = ["CfgNode", "CN"]
