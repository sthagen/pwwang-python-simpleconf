from __future__ import annotations

from pathlib import Path
from importlib import import_module
from types import ModuleType
from typing import Any

from .exceptions import FormatNotSupported
from .loaders import Loader

POOL_KEY = "_SIMPLECONF_POOL"
META_KEY = "_SIMPLECONF_META"


def config_to_ext(conf: Any) -> str:
    """Find the extension(flag) of the configuration"""
    if isinstance(conf, dict):
        return "dict"

    conf = Path(conf)
    out = conf.suffix.lstrip(".").lower()
    if not out and conf.name.lower().endswith("rc"):
        out = "rc"

    if out in ("ini", "rc", "cfg", "conf", "config"):
        return "ini"

    if out == "yml":
        return "yaml"

    return out


def get_loader(ext: str | Loader) -> Loader:
    """Get the loader for the extension"""
    if isinstance(ext, Loader):
        return ext

    if ext == "dict":
        from .loaders.dict import DictLoader
        return DictLoader()

    if ext == "dicts":
        from .loaders.dict import DictsLoader
        return DictsLoader()

    if ext == "env":
        from .loaders.env import EnvLoader
        return EnvLoader()

    if ext == "envs":
        from .loaders.env import EnvsLoader
        return EnvsLoader()

    if ext == "ini":
        from .loaders.ini import IniLoader
        return IniLoader()

    if ext == "inis":
        from .loaders.ini import InisLoader
        return InisLoader()

    if ext == "json":
        from .loaders.json import JsonLoader
        return JsonLoader()

    if ext == "jsons":
        from .loaders.json import JsonsLoader
        return JsonsLoader()

    if ext == "osenv":
        from .loaders.osenv import OsenvLoader
        return OsenvLoader()

    if ext == "toml":
        from .loaders.toml import TomlLoader
        return TomlLoader()

    if ext == "tomls":
        from .loaders.toml import TomlsLoader
        return TomlsLoader()

    if ext == "yaml":
        from .loaders.yaml import YamlLoader
        return YamlLoader()

    if ext == "yamls":
        from .loaders.yaml import YamlsLoader
        return YamlsLoader()

    raise FormatNotSupported(f"{ext} is not supported.")


def require_package(package: str, *fallbacks: str) -> ModuleType:
    """Require the package and return the module"""
    try:
        return import_module(package)
    except ModuleNotFoundError:
        for fallback in fallbacks:
            try:
                return import_module(fallback)
            except ModuleNotFoundError:
                pass

        if fallbacks:
            raise ImportError(
                f"Neither '{package}' nor its fallbacks "
                f"`{', '.join(fallbacks)}` is installed."
            ) from None
        else:
            raise ImportError(f"'{package}' is not installed.") from None
