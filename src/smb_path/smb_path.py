from collections.abc import Generator
from io import TextIOWrapper
from os import stat_result
from pathlib import Path, PosixPath, WindowsPath
from typing import Union

import smbclient


class SmbPath:
    def open(  # noqa A003
        self,
        mode: str = "r",
        buffering: int = -1,
        encoding: Union[str, None] = None,
        errors: Union[str, None] = None,
        newline: Union[str, None] = None,
    ) -> TextIOWrapper:
        return smbclient.open_file(
            str(self), mode=mode, buffering=buffering, encoding=encoding, errors=errors, newline=newline
        )

    def stat(self, *, follow_symlinks: bool = True) -> stat_result:
        return smbclient.stat(str(self), follow_symlinks=follow_symlinks)

    def iterdir(self) -> Generator:
        dir_list = smbclient.listdir(str(self))
        for el in dir_list:
            yield Path(str(self / el))

    def mkdir(self, *args, **kwargs):
        raise NotImplementedError("Function not implemented for SmbPath")

    def rmdir(self, *args, **kwargs):
        raise NotImplementedError("Function not implemented for SmbPath")

    def touch(self, *args, **kwargs):
        raise NotImplementedError("Function not implemented for SmbPath")

    def chmod(self, *args, **kwargs):
        raise NotImplementedError("Function not implemented for SmbPath")

    def unlink(self, *args, **kwargs):
        raise NotImplementedError("Function not implemented for SmbPath")

    def rename(self, *args, **kwargs):
        raise NotImplementedError("Function not implemented for SmbPath")

    def replace(self, *args, **kwargs):
        raise NotImplementedError("Function not implemented for SmbPath")

    def symlink_to(self, *args, **kwargs):
        raise NotImplementedError("Function not implemented for SmbPath")

    def hardlink_to(self, *args, **kwargs):
        raise NotImplementedError("Function not implemented for SmbPath")


class SmbWindowsPath(SmbPath, WindowsPath):
    pass


class SmbPosixPath(SmbPath, PosixPath):
    pass
