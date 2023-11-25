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


def test_smb_path_init_from_str():
    path_string = "//filshr33.us.evilcorp.com/myShare/myDir/"

    path = Path(path_string)

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


def test_not_implemented():
    path = Path("//filshr33.us.evilcorp.com/myShare/newDir")

    with pytest.raises(NotImplementedError):
        path.mkdir(parents=False, exist_ok=True)


@pytest.mark.parametrize(
    "path_func, smb_path_func",
    [
        (Path.open, SmbPath.open),
        (Path.stat, SmbPath.stat),
        (Path.iterdir, SmbPath.iterdir),
    ],
    ids=["open", "stat", "iterdir"],
)
def test_function_signatures(path_func, smb_path_func):
    path_params = inspect.signature(path_func).parameters
    smb_path_params = inspect.signature(smb_path_func).parameters

    for p_param_name, smbp_param_name in zip(path_params, smb_path_params):
        p_param = path_params[p_param_name]
        smbp_param = smb_path_params[smbp_param_name]

        assert p_param.name == smbp_param.name
        assert p_param.default == smbp_param.default
