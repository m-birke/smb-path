# `smb-path` Changelog

## 0.6.0 (2025-05-16)

- Implemented `glob`

## 0.5.1 (2025-01-24)

- Support Python 3.13 (No code changes necessary)

## 0.5.0 (2024-03-03)

- Implemented `mkdir`, `rmdir`, `unlink`, `rename`, `symlink_to`, `replace`
- Windows tested

## 0.4.0 (2023-10-20)

- Support for Python 3.12
- Additional tests

## 0.3.0 (2023-10-19)

- Support for Python 3.7, 3.8, 3.9, 3.10
- Bugfix: Make sure that not implemented functions really raise NotImplementedError
- Setup CI

## 0.2.0 (2023-10-17)

- Raise not implemented error for functions which would need an alternative implementation with smb protocol

## 0.1.0 (2023-10-16)

- First test release
- No CI/CD in place
