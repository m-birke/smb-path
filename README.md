# smb-path

[![PyPI - Version](https://img.shields.io/pypi/v/smb-path.svg)](https://pypi.org/project/smb-path)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/smb-path.svg)](https://pypi.org/project/smb-path)

-----

**Table of Contents**

- [About](#about)
- [Installation](#installation)
- [Usage](#usage)
- [Compatibility](#compatibility)
- [License](#license)

## About

Many tools make use of `pathlib.Path` internally. This is a problem if the files are located on a fileshare. `smb-path` provides wrapper of `Path` which acts accordingly but using the SMB protocol for file operations instead of the local hosts file system. Atm. `smb-path` focuses on pure reading of the data. The SMB protocol implementation of [smbprotocol](https://pypi.org/project/smbprotocol/) is used.

All the utility functions of `Path` should work for `SmbPath` as well (like the `/` operator, `with_suffix`, `parents`, etc.).

Currently the following SMB dependent functions are implemented:

- `open` (and hence dependent funtions like `read_bytes`, etc.)
- `stat` (and hence dependent functions like `lstat`, `is_file`, `is_dir`, `exists`, etc.)
- `iterdir`

In future versions, some functions probably get overwritten with a dummy since functions like `resolve` have no use for a SMB path.

Missing write operations with current version (and questionable whether all of them will come) are:

- `touch`
- `mkdir`
- `rmdir`
- `chmod`
- `unlink`
- `rename`
- `replace`
- `symlink_to`
- `hardlink_to`

## Installation

```console
pip install smb-path
```

## Usage

`smb-path` just needs to be installed. After the installation, you just use `Path()` to instantiate a `SmbPath`. It is checked whether the provided path string applies to the regex pattern `r"(//|\\\\)([a-z0-9]+)((\.[a-z0-9]+)*)(\.[a-z]+){1}"`.

The path string

- must start with `//` or `\\`
- must continue with a server name, a-z and 0-9 allowed, eg. `filshr33`
- optionally an arbitrary number of periods separated by a `.`, a-z and 0-9 allowed, eg. `.us.dieterscompany`
- must continue with an url closing with `.` then a-z, eg. `.com`
- can contain trailing fileshare names, directories or files, eg. `/myShare/myDir/myFile.txt`

Hence `//filshr33.us.dieterscompany.com/myShare/myDir/myFile.txt` would be a valid SMB path.

**If the pattern does not match, a `Path` object like you are used to it is returned** (`WindowsPath` or `PosixPath`).

### SMB Configuration

Use `smbclient.ClientConfig` to configure the SMB connection. Eg. `smbclient.ClientConfig(username="itsme", password="myPW")`. Refer to [smbprotocol](https://pypi.org/project/smbprotocol/) for further information.

## Compatibility

Tested with installation into a `python -m venv` virtual environment.

TODO

| OS      | Python | Supported |
| ------- | ------ | --------- |
| Windows | 3.11   | ✅        |
| Windows |        | ❌        |
| Linux   | 3.11   | ✅        |
| Linux   |        | ❌        |

## License

`smb-path` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
