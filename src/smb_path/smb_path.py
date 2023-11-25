from collections.abc import Generator
from io import TextIOWrapper
from os import stat_result
from pathlib import Path, PosixPath, WindowsPath
from typing import Self

import smbclient


class SmbPath:
    def open(  # noqa A003
        self: Self,
        mode: str = "r",
        buffering: int = -1,
        encoding: str | None = None,
        errors: str | None = None,
        newline: str | None = None,
    ) -> TextIOWrapper:
        return smbclient.open_file(
            str(self), mode=mode, buffering=buffering, encoding=encoding, errors=errors, newline=newline
        )

    def stat(self, *, follow_symlinks: bool = True) -> stat_result:
        return smbclient.stat(str(self), follow_symlinks=follow_symlinks)

    def iterdir(self) -> Generator[Self, None, None]:
        dir_list = smbclient.listdir(str(self))
        for el in dir_list:
            yield Path(str(self / el))


class SmbWindowsPath(SmbPath, WindowsPath):
    pass


class SmbPosixPath(SmbPath, PosixPath):
    pass
