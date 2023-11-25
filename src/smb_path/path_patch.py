import os
import re
import sys
from pathlib import Path

import wrapt

from smb_path.smb_path import SmbPath, SmbPosixPath, SmbWindowsPath

if sys.version_info >= (3, 12):

    @wrapt.when_imported("pathlib")
    def patch_path_constructor(pathlib):
        def wrapt_new(original_new, _instance, args, _kwargs):
            cls = args[0]
            user_args = args[1:]

            if cls is not Path:
                return original_new(*args)

            if not user_args:
                return original_new(*args)

            if isinstance(user_args[0], str):
                # check for server URL pattern of first arg
                if not re.match(r"(//|\\\\)([a-z0-9]+)((\.[a-z0-9]+)*)(\.[a-z]+){1}", user_args[0]):
                    return original_new(*args)  # not smb

            elif not isinstance(user_args[0], SmbPath):
                return original_new(*args)

            cls = SmbWindowsPath if os.name == "nt" else SmbPosixPath

            return object.__new__(cls)

        wrapt.wrap_function_wrapper(pathlib.Path, "__new__", wrapt_new)

else:

    @wrapt.when_imported("pathlib")
    def patch_path_constructor(pathlib):
        def wrapt_new(original_new, _instance, args, _kwargs):
            cls = args[0]
            user_args = args[1:]

            if cls is not Path:
                return original_new(*args)

            if not user_args:
                return original_new(*args)

            if isinstance(user_args[0], str):
                # check for server URL pattern of first arg
                if not re.match(r"(//|\\\\)([a-z0-9]+)((\.[a-z0-9]+)*)(\.[a-z]+){1}", user_args[0]):
                    return original_new(*args)  # not smb

            elif not isinstance(user_args[0], SmbPath):
                return original_new(*args)

            cls = SmbWindowsPath if os.name == "nt" else SmbPosixPath

            self = cls._from_parts(user_args)
            return self

        wrapt.wrap_function_wrapper(pathlib.Path, "__new__", wrapt_new)
