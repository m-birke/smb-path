import smb_path.path_patch  # noqa F401

import inspect
import sys

import pytest

from pathlib import Path
from smb_path.smb_path import SmbPath

import smbprotocol.exceptions as smb_exceptions


def _assert_signatures_match(path_func, smb_path_func):
    path_params = inspect.signature(path_func).parameters
    smb_path_params = inspect.signature(smb_path_func).parameters

    assert len(path_params) == len(smb_path_params)

    for p_param_name, smbp_param_name in zip(path_params, smb_path_params, strict=True):
        p_param = path_params[p_param_name]
        smbp_param = smb_path_params[smbp_param_name]

        assert p_param.name == smbp_param.name
        assert p_param.default == smbp_param.default


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
        ("//file_share.local/theirshare/theirdir/log.txt"),
        ("//file_share/theirshare/theirdir/log.txt"),
    ],
    ids=["letters", "numbers", "hyphen", "underscore", "local", "no_tld"],
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
    _assert_signatures_match(path_func, smb_path_func)


@pytest.mark.skipif(sys.version_info < (3, 12), reason="Path.walk was added in Python 3.12")
def test_walk_signature():
    _assert_signatures_match(Path.walk, SmbPath.walk)  # type: ignore[attr-defined]


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


# ---------------------------------------------------------------------------
# walk
# ---------------------------------------------------------------------------

pytestmark_walk = pytest.mark.skipif(sys.version_info < (3, 12), reason="Path.walk was added in Python 3.12")

_ROOT = "//filshr33.us.evilcorp.com/myShare"


class _FakeDirEntry:
    """Minimal stand in for smbclient.SMBDirEntry."""

    def __init__(self, name: str, *, is_dir: bool = False, is_symlink: bool = False):
        self.name = name
        self._is_dir = is_dir
        self._is_symlink = is_symlink

    def is_dir(self, follow_symlinks: bool = True) -> bool:  # noqa FBT001, FBT002
        if self._is_symlink:
            return self._is_dir and follow_symlinks
        return self._is_dir

    def is_symlink(self) -> bool:
        return self._is_symlink


def _dir(name: str) -> _FakeDirEntry:
    return _FakeDirEntry(name, is_dir=True)


def _file(name: str) -> _FakeDirEntry:
    return _FakeDirEntry(name)


def _link_dir(name: str) -> _FakeDirEntry:
    return _FakeDirEntry(name, is_dir=True, is_symlink=True)


@pytest.fixture
def fake_scandir(monkeypatch):
    """Install a fake smbclient.scandir backed by an in-memory tree.

    Keys are path strings with normalized separators, values are entry lists or an
    exception instance to raise instead of listing.
    """
    calls = []

    def _install(tree: dict):
        def scandir(path, *args, **kwargs):  # noqa ARG001
            calls.append(path)
            key = str(path).replace("\\", "/")
            entries = tree[key]
            if isinstance(entries, Exception):
                raise entries
            yield from entries

        monkeypatch.setattr("smb_path.smb_path.smbclient.scandir", scandir)
        return calls

    _install.calls = calls
    return _install


def _walk(root: str = _ROOT, **kwargs):
    return list(Path(root).walk(**kwargs))  # type: ignore[attr-defined]


def _names(result):
    """Reduce walk output to (posix dirpath, dirnames, filenames) for easy comparison."""
    return [(str(dirpath).replace("\\", "/"), dirnames, filenames) for dirpath, dirnames, filenames in result]


@pytest.fixture
def simple_tree(fake_scandir):
    return fake_scandir(
        {
            _ROOT: [_file("a.txt"), _dir("sub"), _dir("empty")],
            f"{_ROOT}/sub": [_file("b.txt"), _dir("deep")],
            f"{_ROOT}/sub/deep": [_file("c.txt")],
            f"{_ROOT}/empty": [],
        }
    )


@pytestmark_walk
def test_walk_top_down(simple_tree):  # noqa ARG001
    assert _names(_walk()) == [
        (_ROOT, ["sub", "empty"], ["a.txt"]),
        (f"{_ROOT}/sub", ["deep"], ["b.txt"]),
        (f"{_ROOT}/sub/deep", [], ["c.txt"]),
        (f"{_ROOT}/empty", [], []),
    ]


@pytestmark_walk
def test_walk_yields_smb_paths(simple_tree):  # noqa ARG001
    for dirpath, _, _ in _walk():
        assert isinstance(dirpath, SmbPath)


@pytestmark_walk
def test_walk_bottom_up(simple_tree):  # noqa ARG001
    assert _names(_walk(top_down=False)) == [
        (f"{_ROOT}/sub/deep", [], ["c.txt"]),
        (f"{_ROOT}/sub", ["deep"], ["b.txt"]),
        (f"{_ROOT}/empty", [], []),
        (_ROOT, ["sub", "empty"], ["a.txt"]),
    ]


@pytestmark_walk
def test_walk_top_down_pruning(simple_tree):  # noqa ARG001
    visited = []
    for dirpath, dirnames, _ in Path(_ROOT).walk():  # type: ignore[attr-defined]
        visited.append(str(dirpath).replace("\\", "/"))
        if dirnames == ["sub", "empty"]:
            dirnames.remove("sub")

    assert visited == [_ROOT, f"{_ROOT}/empty"]


@pytestmark_walk
def test_walk_bottom_up_pruning_has_no_effect(simple_tree):  # noqa ARG001
    visited = []
    for dirpath, dirnames, _ in Path(_ROOT).walk(top_down=False):  # type: ignore[attr-defined]
        visited.append(str(dirpath).replace("\\", "/"))
        dirnames.clear()

    assert visited == [f"{_ROOT}/sub/deep", f"{_ROOT}/sub", f"{_ROOT}/empty", _ROOT]


@pytestmark_walk
def test_walk_is_lazy(simple_tree):
    walker = Path(_ROOT).walk()

    assert simple_tree == []

    next(walker)

    assert len(simple_tree) == 1


@pytest.fixture
def symlink_tree(fake_scandir):
    return fake_scandir(
        {
            _ROOT: [_file("a.txt"), _link_dir("link")],
            f"{_ROOT}/link": [_file("b.txt")],
        }
    )


@pytestmark_walk
def test_walk_symlink_dir_not_followed(symlink_tree):  # noqa ARG001
    """Like pathlib (and unlike os.walk), a non followed symlink dir is a filename."""
    assert _names(_walk()) == [(_ROOT, [], ["a.txt", "link"])]


@pytestmark_walk
def test_walk_symlink_dir_followed(symlink_tree):  # noqa ARG001
    assert _names(_walk(follow_symlinks=True)) == [
        (_ROOT, ["link"], ["a.txt"]),
        (f"{_ROOT}/link", [], ["b.txt"]),
    ]


@pytest.fixture
def error_tree(fake_scandir):
    return fake_scandir(
        {
            _ROOT: [_dir("denied"), _dir("ok")],
            f"{_ROOT}/denied": smb_exceptions.SMBOSError(ntstatus=0xC0000022, filename=f"{_ROOT}/denied"),
            f"{_ROOT}/ok": [_file("a.txt")],
        }
    )


@pytestmark_walk
def test_walk_errors_ignored_by_default(error_tree):  # noqa ARG001
    assert _names(_walk()) == [
        (_ROOT, ["denied", "ok"], []),
        (f"{_ROOT}/ok", [], ["a.txt"]),
    ]


@pytestmark_walk
def test_walk_on_error_called(error_tree):  # noqa ARG001
    errors = []

    result = _walk(on_error=errors.append)

    assert len(errors) == 1
    assert isinstance(errors[0], OSError)
    assert len(result) == 2


@pytestmark_walk
def test_walk_on_error_may_abort(error_tree):  # noqa ARG001
    def reraise(error):
        raise error

    with pytest.raises(OSError):
        _walk(on_error=reraise)


@pytestmark_walk
def test_walk_unlistable_root_yields_nothing(fake_scandir):
    fake_scandir({_ROOT: smb_exceptions.SMBOSError(ntstatus=0xC0000034, filename=_ROOT)})

    assert _walk() == []
