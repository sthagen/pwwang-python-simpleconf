from __future__ import annotations

import io
import re
from pathlib import Path
from importlib import import_module
from types import ModuleType
from typing import Any, Dict, List

from .exceptions import FormatNotSupported
from .loaders import Loader

POOL_KEY = "_SIMPLECONF_POOL"
META_KEY = "_SIMPLECONF_META"

_LOADER_DIRECTIVE_RE = re.compile(
    r"^\s*(?:#|;|//)\s*simpleconf-loader:\s*(\S+)",
    re.IGNORECASE,
)

_LOADENV_DIRECTIVE_RE = re.compile(
    r"^\s*(?:#|;|//)\s*simpleconf-loadenv(?::\s*(.+))?$",
    re.IGNORECASE,
)


def _read_first_lines(conf: Any) -> List[str]:
    """Read the first few lines of a config file for directive detection.

    Args:
        conf: The configuration source.

    Returns:
        A list of lines (up to 5) from the beginning of the file,
        or an empty list if *conf* is not a readable file.
    """
    if isinstance(conf, dict) or hasattr(conf, "read"):
        return []

    path = Path(conf)
    if not path.exists():
        return []

    try:
        return path.read_text(errors="replace").split("\n")[:5]
    except Exception:
        return []


def detect_loader_directive(conf: Any, current_ext: str) -> str:
    """Detect if the first few lines of a config file contain a loader
    directive.

    Supports comment styles::

        # simpleconf-loader: toml.liq
        # simpleconf-loader: liq
        # simpleconf-loader: liquid
        ; simpleconf-loader: ini.liq
        // simpleconf-loader: json.j2

    Short aliases ``liq``/``liquid`` and ``j2``/``jinja``/``jinja2`` are
    expanded relative to the base format of *current_ext*.
    Any other value is used verbatim as the loader extension.

    Args:
        conf: The configuration source.  Dicts and stream objects are
            ignored (returns *current_ext* unchanged).
        current_ext: The extension string already derived from the filename.

    Returns:
        The overriding extension string, or *current_ext* when no directive
        is present.
    """
    lines = _read_first_lines(conf)
    if not lines:
        return current_ext

    for line in lines:
        match = _LOADER_DIRECTIVE_RE.match(line)
        if not match:
            continue

        directive = match.group(1).lower()

        # Derive the base format name
        # (strip any existing template suffix)
        parts = current_ext.split(".")
        base_ext = parts[0] if parts[-1] in ("j2", "liq") else current_ext

        if directive in ("liq", "liquid"):
            return base_ext + ".liq"

        if directive in ("j2", "jinja", "jinja2"):
            return base_ext + ".j2"

        # Treat as an explicit loader extension name
        return directive

    return current_ext


def detect_loadenv_directive(conf: Any) -> str | None:
    """Detect if the first few lines of a config file contain a loadenv
    directive.

    Supports both a bare directive (defaults to ``./.env``) and a path::

        # simpleconf-loadenv
        # simpleconf-loadenv: /path/to/.env
        ; simpleconf-loadenv: ../shared/.env
        // simpleconf-loadenv

    The path is resolved relative to the config file's directory.

    Args:
        conf: The configuration source.  Dicts and stream objects are
            ignored (returns ``None``).

    Returns:
        The absolute path to the ``.env`` file, or ``None`` when no
        directive is present.
    """
    lines = _read_first_lines(conf)
    if not lines:
        return None

    for line in lines:
        match = _LOADENV_DIRECTIVE_RE.match(line)
        if not match:
            continue

        raw_path = (match.group(1) or "").strip()
        conf_dir = Path(conf).parent

        if not raw_path:
            return str(conf_dir.resolve() / ".env")

        env_path = Path(raw_path)
        if not env_path.is_absolute():
            env_path = (conf_dir / env_path).resolve()
        return str(env_path)

    return None


def load_dotenv_file(env_path: str) -> Dict[str, str]:
    """Load environment variables from a ``.env`` file.

    Uses ``python-dotenv`` to parse the file.  Returns only the variables
    defined in the file — does **not** modify ``os.environ``.

    Args:
        env_path: Path to the ``.env`` file.

    Returns:
        A dict of variable names to values.  Returns an empty dict when
        the file does not exist.
    """
    dotenv = require_package("dotenv")
    dotenv_file = Path(env_path)
    if not dotenv_file.exists():
        return {}
    content = dotenv_file.read_text()
    sio = io.StringIO(content)
    return dict(dotenv.dotenv_values(stream=sio))


def config_to_ext(conf: Any, secondary: bool = True) -> str:
    """Find the extension(flag) of the configuration"""
    if isinstance(conf, dict):
        return "dict"

    conf = Path(conf)
    out = conf.suffix.lstrip(".").lower()
    if out in ('j2', 'jinja2', 'jinja'):
        # x.toml.j2
        return config_to_ext(conf.stem) + '.j2'
    if out in ('liq', 'liquid'):
        # x.toml.liq
        return config_to_ext(conf.stem) + '.liq'

    if secondary:
        secondary_suffix = conf.with_suffix("").suffix.lstrip(".").lower()
        # x.j2.toml
        if secondary_suffix in ('j2', 'jinja2', 'jinja'):
            return config_to_ext(conf, secondary=False) + '.j2'
        if secondary_suffix in ('liq', 'liquid'):
            return config_to_ext(conf, secondary=False) + '.liq'

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

    if ext == "env.j2":
        from .loaders.env import EnvJ2Loader
        return EnvJ2Loader()

    if ext == "env.liq":
        from .loaders.env import EnvLiqLoader
        return EnvLiqLoader()

    if ext == "envs":
        from .loaders.env import EnvsLoader
        return EnvsLoader()

    if ext == "ini":
        from .loaders.ini import IniLoader
        return IniLoader()

    if ext == "ini.j2":
        from .loaders.ini import IniJ2Loader
        return IniJ2Loader()

    if ext == "ini.liq":
        from .loaders.ini import IniLiqLoader
        return IniLiqLoader()

    if ext == "inis":
        from .loaders.ini import InisLoader
        return InisLoader()

    if ext == "json":
        from .loaders.json import JsonLoader
        return JsonLoader()

    if ext == "json.j2":
        from .loaders.json import JsonJ2Loader
        return JsonJ2Loader()

    if ext == "json.liq":
        from .loaders.json import JsonLiqLoader
        return JsonLiqLoader()

    if ext == "jsons":
        from .loaders.json import JsonsLoader
        return JsonsLoader()

    if ext == "osenv":
        from .loaders.osenv import OsenvLoader
        return OsenvLoader()

    if ext == "toml":
        from .loaders.toml import TomlLoader
        return TomlLoader()

    if ext == "toml.j2":
        from .loaders.toml import TomlJ2Loader
        return TomlJ2Loader()

    if ext == "toml.liq":
        from .loaders.toml import TomlLiqLoader
        return TomlLiqLoader()

    if ext == "tomls":
        from .loaders.toml import TomlsLoader
        return TomlsLoader()

    if ext == "yaml":
        from .loaders.yaml import YamlLoader
        return YamlLoader()

    if ext == "yaml.j2":
        from .loaders.yaml import YamlJ2Loader
        return YamlJ2Loader()

    if ext == "yaml.liq":
        from .loaders.yaml import YamlLiqLoader
        return YamlLiqLoader()

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
