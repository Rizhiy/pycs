from pathlib import Path

import pytest

from ntc import CN, MissingRequired, NodeFrozenError, SaveError, SchemaError, SchemaFrozenError, TypeMismatch
from tests.data.base_cfg import BaseClass, cfg
from tests.data.subclass_class import SubClass

DATA_DIR = Path(__file__).parent / "data"


def test_good():
    good = CN.load(DATA_DIR / "good.py")
    assert good.NAME == "Name"


def test_bad():
    with pytest.raises(TypeMismatch):
        CN.load(DATA_DIR / "bad.py")


def test_missing():
    with pytest.raises(MissingRequired):
        CN.load(DATA_DIR / "missing.py")


def test_bad_attr():
    with pytest.raises(SchemaFrozenError):
        CN.load(DATA_DIR / "bad_attr.py")


def test_subclass():
    subclass = CN.load(DATA_DIR / "subclass.py")
    assert isinstance(subclass.CLASS, SubClass)


def test_bad_class():
    with pytest.raises(TypeMismatch):
        CN.load(DATA_DIR / "bad_class.py")


def test_list():
    lst = CN.load(DATA_DIR / "list.py")
    assert lst.LIST == [3, 2, 1]


def test_node():
    node = CN.load(DATA_DIR / "node.py")
    assert len(node.CLASSES) == 1
    assert isinstance(node.CLASSES.ONE, BaseClass)


def test_bad_node():
    with pytest.raises(SchemaError):
        CN.load(DATA_DIR / "bad_node.py")


def test_save(tmp_path):
    good = CN.load(DATA_DIR / "good.py")
    good.save(tmp_path / "good2.py")

    good2 = CN.load(tmp_path / "good2.py")
    assert good == good2


def test_save_unfrozen(tmp_path):
    good = CN.load(DATA_DIR / "good.py")
    good.unfreeze()
    good.freeze()
    with pytest.raises(SaveError):
        good.save(tmp_path / "good2.py")


def test_save_base(tmp_path):
    with pytest.raises(SaveError):
        cfg.save(tmp_path / "base_cfg2.py")


def test_freeze_loaded():
    good = CN.load(DATA_DIR / "good.py")
    with pytest.raises(NodeFrozenError):
        # first level assignment
        good.NAME = "bar"
    with pytest.raises(NodeFrozenError):
        # nested assignment
        good.DICT.FOO = "bar"
    with pytest.raises(NodeFrozenError):
        # new attribute
        good.BAR = "bar"


def test_node_subclass():
    node = CN.load(DATA_DIR / "node_subclass.py")
    assert issubclass(node.SUBCLASSES.ONE, BaseClass)


def test_bad_node_subclass():
    with pytest.raises(SchemaError):
        CN.load(DATA_DIR / "bad_node_subclass.py")


def test_bad_node_instance():
    with pytest.raises(SchemaError):
        CN.load(DATA_DIR / "bad_node_instance.py")


def test_transform():
    transform = CN.load(DATA_DIR / "transform.py")
    assert transform.DICT.FOO == "bar"


def test_validate():
    with pytest.raises(AssertionError):
        CN.load(DATA_DIR / "validate.py")


def test_transform_inheritance():
    transform = CN.load(DATA_DIR / "transform_inheritance.py")
    assert transform.DICT.FOO == "baz"


def test_validate_inheritance():
    with pytest.raises(AssertionError):
        CN.load(DATA_DIR / "validate_inheritance.py")