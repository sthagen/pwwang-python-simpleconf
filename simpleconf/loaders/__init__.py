from __future__ import annotations

import os
from abc import ABC, abstractmethod
from typing import Any, Callable, List, Dict
from pathlib import Path

from diot import Diot
from panpath import PanPath
from ..caster import (
    cast,
    cast_value,
    int_caster,
    float_caster,
    bool_caster,
    none_caster,
    python_caster,
    py_caster,
    json_caster,
    toml_caster,
)

_ENV_CASTERS = [
    int_caster,
    float_caster,
    bool_caster,
    none_caster,
    python_caster,
    py_caster,
    json_caster,
    toml_caster,
]


class Loader(ABC):

    CASTERS: List[Callable[[str, bool], Any]] | None = None

    def __init__(self) -> None:
        self.env_vars: Dict[str, str] = {}

    @staticmethod
    def _convert_path(conf: str | Path) -> Path:
        """Convert the conf to Path if it is a string"""
        if isinstance(conf, (str, Path)):
            return PanPath(conf)
        return conf

    @abstractmethod
    def loading(self, conf: Any, ignore_nonexist: bool) -> Dict[str, Any]:
        """Load the configuration from the path or configurations"""

    @abstractmethod
    async def a_loading(self, conf: Any, ignore_nonexist: bool) -> Dict[str, Any]:
        """Asynchronously load the configuration from the path or configurations"""

    @classmethod
    def _convert(cls, conf: Any, loaded: Any) -> Diot:
        """Convert the loaded configuration to Diot"""
        if cls.CASTERS:
            loaded = cast(loaded, cls.CASTERS)

        return Diot(loaded)

    def _resolve_env_vars(self, loaded: Diot) -> Diot:
        """Resolve ``$env:VAR`` references in loaded config values.

        Called after ``_convert()`` (i.e., after casters have been applied).
        Recursively walks the config and replaces string values matching
        ``$env:KEY`` with the corresponding environment variable.

        Lookup order:
            1. ``self.env_vars`` (loaded from ``.env`` file via directive)
            2. ``os.environ`` (system environment variables)

        ``$env:KEY:default:<value>`` falls back to ``<value>`` when the
        variable is not found (modifiers ``required``, ``optional-asis`` and
        ``optional-empty`` control the not-found behavior otherwise).

        Resolved values are re-cast through :attr:`CASTERS`.

        Returns the mutated Diot for chaining.
        """
        dict_type = type({})

        KNOWN_MODIFIERS = frozenset(
            {"required", "optional-asis", "optional-empty"}
        )

        def _walk(value):
            if isinstance(value, dict_type):
                for k, v in value.items():
                    value[k] = _walk(v)
                return value
            if isinstance(value, str) and value.startswith("$env:"):
                rest = value[5:]
                default = None
                if ":default:" in rest:
                    # $env:VAR:default:<value> — split on first occurrence so
                    # the default itself may contain colons
                    var_name, _, default = rest.partition(":default:")
                    modifier = "required"
                elif ":" in rest:
                    var_name, modifier = rest.rsplit(":", 1)
                    if modifier not in KNOWN_MODIFIERS:
                        # Unknown modifier — treat whole string as var name
                        var_name, modifier = rest, "required"
                else:
                    var_name, modifier = rest, "required"

                resolved = self.env_vars.get(var_name)
                if resolved is None:
                    resolved = os.environ.get(var_name)

                if resolved is not None:
                    return cast_value(resolved, _ENV_CASTERS)

                # Not found — use the default value if given
                if default is not None:
                    return cast_value(default, _ENV_CASTERS)

                # Not found — behavior depends on modifier
                if modifier == "optional-empty":
                    return ""
                if modifier == "optional-asis":
                    return f"$env:{var_name}"
                # required (default)
                raise ValueError(
                    f"Environment variable '{var_name}' not found."
                )
            return value

        return _walk(loaded)

    @classmethod
    def _convert_with_profiles(cls, conf: Any, loaded: Any) -> Diot:
        """Convert the loaded configuration with profiles to Diot"""
        return Diot(loaded)

    def _exists(self, conf: str | Path, ignore_exist: bool) -> bool:
        """Check if the configuration file exists"""
        path = self.__class__._convert_path(conf)
        exists = path.exists()
        if not ignore_exist and not exists:
            raise FileNotFoundError(f"{conf} does not exist")
        return exists

    async def _a_exists(self, conf: str | Path, ignore_exist: bool) -> bool:
        """Asynchronously check if the configuration file exists"""
        path = self.__class__._convert_path(conf)
        exists = await path.a_exists()  # type: ignore[attr-defined]
        if not ignore_exist and not exists:
            raise FileNotFoundError(f"{conf} does not exist")
        return exists

    def load(self, conf: Any, ignore_nonexist: bool = False) -> Diot:
        """Load the configuration from the path or configurations and cast
        values

        Args:
            conf: The configuration file to load

        Returns:
            The Diot object
        """
        path = self.__class__._convert_path(conf)
        loaded = self.loading(path, ignore_nonexist)
        return self._resolve_env_vars(self.__class__._convert(conf, loaded))

    async def a_load(self, conf: Any, ignore_nonexist: bool = False) -> Diot:
        """Asynchronously load the configuration from the path or configurations
        and cast values

        Args:
            conf: The configuration file to load

        Returns:
            The Diot object
        """
        path = self.__class__._convert_path(conf)
        loaded = await self.a_loading(path, ignore_nonexist)
        return self._resolve_env_vars(self.__class__._convert(conf, loaded))

    def load_with_profiles(  # type: ignore[override]
        self,
        conf: Any,
        ignore_nonexist: bool = False,
    ) -> Diot:
        """Load the configuration from the path or configurations with profiles
        and cast values

        Args:
            conf: The configuration file to load

        Returns:
            The Diot object
        """
        path = self.__class__._convert_path(conf)
        loaded = self.loading(path, ignore_nonexist)
        return self._resolve_env_vars(
            self.__class__._convert_with_profiles(conf, loaded)
        )

    async def a_load_with_profiles(  # type: ignore[override]
        self,
        conf: Any,
        ignore_nonexist: bool = False,
    ) -> Diot:
        """Asynchronously load the configuration from the path or configurations
        with profiles and cast values

        Args:
            conf: The configuration file to load

        Returns:
            The Diot object
        """
        path = self.__class__._convert_path(conf)
        loaded = await self.a_loading(path, ignore_nonexist)
        return self._resolve_env_vars(
            self.__class__._convert_with_profiles(conf, loaded)
        )


class NoConvertingPathMixin(ABC):
    """String loader base class"""

    @staticmethod
    def _convert_path(conf: str) -> str:
        return conf

    async def a_loading(self, conf: Any, ignore_nonexist: bool) -> Dict[str, Any]:
        """Asynchronously load the configuration from a toml file"""
        return self.loading(conf, ignore_nonexist)  # type: ignore[attr-defined]


class LoaderModifierMixin(ABC):
    """Loader mixin class with content modifier"""

    def _modifier(self, content: str | bytes) -> str | bytes:
        """Modify the content of the configuration file before loading"""
        return content


class J2ModifierMixin(LoaderModifierMixin):
    """Loader mixin class with Jinja2 content modifier"""

    def _modifier(self, content: str | bytes) -> str | bytes:
        """Modify the content of the configuration file before loading"""
        from jinja2 import Template
        env_vars = getattr(self, "env_vars", {})
        casted_env = {
            k: cast_value(v, _ENV_CASTERS) for k, v in env_vars.items()
        }
        return Template(content).render(env=casted_env)  # type: ignore


class LiqModifierMixin(LoaderModifierMixin):
    """Loader mixin class with Liquid content modifier"""

    def _modifier(self, content: str | bytes) -> str | bytes:
        """Modify the content of the configuration file before loading"""
        from liquid import Liquid  # type: ignore[import]
        str_content = content.decode() if isinstance(content, bytes) else content
        liq = Liquid(str_content, from_file=False, mode="wild")  # type: ignore
        env_vars = getattr(self, "env_vars", {})
        casted_env = {
            k: cast_value(v, _ENV_CASTERS) for k, v in env_vars.items()
        }
        return liq.render(env=casted_env)  # type: ignore
