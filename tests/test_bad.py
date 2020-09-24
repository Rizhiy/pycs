from pathlib import Path

import pytest

from ntc import CN, MissingRequired, SchemaError, SchemaFrozenError, TypeMismatch

DATA_DIR = Path(__file__).parent / "data" / "bad"


def test_bad():
    with pytest.raises(TypeMismatch):
        CN.load(DATA_DIR / "bad.py")


def test_missing():
    with pytest.raises(MissingRequired):
        CN.load(DATA_DIR / "missing.py")


def test_bad_attr():
    with pytest.raises(SchemaFrozenError):
        CN.load(DATA_DIR / "bad_attr.py")


def test_bad_class():
    with pytest.raises(TypeMismatch):
        CN.load(DATA_DIR / "bad_class.py")


def test_bad_node():
    with pytest.raises(SchemaError):
        CN.load(DATA_DIR / "bad_node.py")


def test_bad_node_subclass():
    with pytest.raises(SchemaError):
        CN.load(DATA_DIR / "bad_node_subclass.py")


def test_bad_node_instance():
    with pytest.raises(SchemaError):
        CN.load(DATA_DIR / "bad_node_instance.py")


def test_inheritance_changes_bad():
    with pytest.raises(MissingRequired):
        CN.load(DATA_DIR / "inheritance_changes_bad.py")


def test_bad_clone():
    with pytest.raises(SchemaError):
        CN.load(DATA_DIR / "bad_clone.py")


def test_bad_inherit():
    with pytest.raises(SchemaError):
        CN.load(DATA_DIR / "bad_inherit_changes.py")


def test_schema_freeze():
    with pytest.raises(SchemaError):
        CN.load(DATA_DIR / "bad_schema.py")


def test_bad_init():
    with pytest.raises(SchemaError):
        CN.load(DATA_DIR / "bad_init.py")