import smb_path.path_patch  # noqa F401

import inspect
import pytest

from pathlib import Path
from smb_path.smb_path import SmbPath


def test_non_smb_path_init_from_str():
    path_string = "C:/Users/Yuan"

    path = Path(path_string)

    assert not isinstance(path, SmbPath)


def test_non_smb_path_init_from_path():
    path_string = "C:/Users/Yuan"

    path1 = Path(path_string)
    path = Path(path1, "Documents")

    assert not isinstance(path, SmbPath)
    assert str(path) == "C:/Users/Yuan/Documents" or str(path) == r"C:\Users\Yuan\Documents"


@pytest.mark.parametrize(
    "smb_path_str",
    [
        ("//filer.us.senez.com/myShare/myDir/"),
        ("//filshr33.eu.ourcorp.com/YourShare/YourDir/log.txt"),
        ("//file-share.eu-pt.minez.com/theirshare/theirdir/log.txt"),
        ("//file_share.eu_nw.p-i.com/theirshare/theirdir/log.txt"),
    ],
    ids=["letters", "numbers", "hyphen", "underscore"],
)
def test_smb_path_init_from_str(smb_path_str: str):
    path = Path(smb_path_str)

    assert isinstance(path, SmbPath)


def test_smb_path_init_from_path():
    path_string = "//filshr33.us.evilcorp.com/myShare/myDir"

    path1 = Path(path_string)
    path = Path(path1, "myFile.txt")

    assert isinstance(path, SmbPath)
    assert (
        str(path) == "//filshr33.us.evilcorp.com/myShare/myDir/myFile.txt"
        or str(path) == r"\\filshr33.us.evilcorp.com\myShare\myDir\myFile.txt"
    )


@pytest.mark.parametrize(
    "path_func, smb_path_func",
    [
        (Path.open, SmbPath.open),
        (Path.stat, SmbPath.stat),
        (Path.iterdir, SmbPath.iterdir),
        (Path.mkdir, SmbPath.mkdir),
        (Path.rmdir, SmbPath.rmdir),
        (Path.unlink, SmbPath.unlink),
        (Path.rename, SmbPath.rename),
        (Path.symlink_to, SmbPath.symlink_to),
        (Path.replace, SmbPath.replace),
        (Path.resolve, SmbPath.resolve),
        (Path.glob, SmbPath.glob),
    ],
    ids=["open", "stat", "iterdir", "mkdir", "rmdir", "unlink", "rename", "symlink", "replace", "resolve", "glob"],
)
def test_function_signatures(path_func, smb_path_func):
    path_params = inspect.signature(path_func).parameters
    smb_path_params = inspect.signature(smb_path_func).parameters

    assert len(path_params) == len(smb_path_params)

    for p_param_name, smbp_param_name in zip(path_params, smb_path_params):
        p_param = path_params[p_param_name]
        smbp_param = smb_path_params[smbp_param_name]

        assert p_param.name == smbp_param.name
        assert p_param.default == smbp_param.default


@pytest.mark.parametrize(
    "path_func, kwargs",
    [
        ("touch", {"mode": 700, "exist_ok": False}),
        ("chmod", {"mode": 700, "follow_symlinks": True}),
        ("hardlink_to", {"target": "foo"}),
    ],
    ids=["touch", "chmod", "hardlink"],
)
def test_not_implemented_functions(path_func, kwargs):
    path = Path("//filshr33.us.evilcorp.com/myShare/newDir")

    func = getattr(path, path_func)

    with pytest.raises(NotImplementedError):
        func(**kwargs)
