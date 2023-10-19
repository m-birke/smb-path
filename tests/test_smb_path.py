import smb_path.path_patch

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
    assert str(path) == "//filshr33.us.evilcorp.com/myShare/myDir/myFile.txt" or str(path) == r"\\filshr33.us.evilcorp.com\myShare\myDir\myFile.txt"
