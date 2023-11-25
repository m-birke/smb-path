from collections.abc import Generator
from io import TextIOWrapper
from os import stat_result
from pathlib import Path, PosixPath, WindowsPath
from typing import Union

import smbclient
import smbprotocol.exceptions as smb_exceptions


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

    def mkdir(self, mode: int = 511, parents: bool = False, exist_ok: bool = False) -> None:  # noqa ARG002
        # TODO implement mode
        try:
            smbclient.mkdir(str(self))
        except smb_exceptions.SMBOSError as e:
            if (not exist_ok) and ("[Error 17]" in str(e)):
                raise e

            if "[Error 2]" in str(e):
                if not parents:
                    raise e
                self.parent.mkdir(parents=True, exist_ok=True)
                self.mkdir(parents=False, exist_ok=exist_ok)

    def rmdir(self) -> None:
        smbclient.rmdir(str(self))

    def touch(self, *args, **kwargs):  # noqa ARG002
        # smbclient does not provide touch function
        msg = "Function not implemented for SmbPath"
        raise NotImplementedError(msg)

    def chmod(self, *args, **kwargs):  # noqa ARG002
        # smbclient does nt provide chmod
        msg = "Function not implemented for SmbPath"
        raise NotImplementedError(msg)

    def unlink(self, missing_ok: bool = False) -> None:
        if not missing_ok:
            smbclient.remove(str(self))
            return None

        try:
            smbclient.remove(str(self))
        except smb_exceptions.SMBOSError as e:
            if "[Error 2]" in str(e):
                return None
            raise e

    def rename(self, *args, **kwargs):  # noqa ARG002
        msg = "Function not implemented for SmbPath"
        raise NotImplementedError(msg)

    def replace(self, *args, **kwargs):  # noqa ARG002
        msg = "Function not implemented for SmbPath"
        raise NotImplementedError(msg)

    def symlink_to(self, *args, **kwargs):  # noqa ARG002
        msg = "Function not implemented for SmbPath"
        raise NotImplementedError(msg)

    def hardlink_to(self, *args, **kwargs):  # noqa ARG002
        msg = "Function not implemented for SmbPath"
        raise NotImplementedError(msg)


class SmbWindowsPath(SmbPath, WindowsPath):
    pass


class SmbPosixPath(SmbPath, PosixPath):
    pass
