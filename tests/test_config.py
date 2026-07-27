from panpath.base import PanPath
import pytest

from simpleconf import Config, ProfileConfig

pytest_plugins = ["tests.fixt_simpleconf"]


def test_nonprofile(ini_file, ini_file_rc, dict_obj):
    config = Config.load(dict_obj)
    assert config.default.a == 1
    assert config.b == 2

    config = Config.load_one(dict_obj)
    assert config.default.a == 1
    assert config.b == 2

    with pytest.warns(UserWarning):
        config = Config.load({"a": {"b": 2}}, ini_file)
    assert config.a == 1
    assert config.b == 2

    config = Config.load_one(ini_file_rc, loader="toml")
    assert config.DEFAULT.a == 7
    assert config.TEST.a == 9

    config = Config.load(ini_file_rc, loader="toml")
    assert config.DEFAULT.a == 7
    assert config.TEST.a == 9

    config = ProfileConfig.load(ini_file_rc, loader="toml")
    assert config.a == 7
    assert config.b == 8


async def test_async_nonprofile(ini_file, ini_file_rc, dict_obj):
    config = await Config.a_load(dict_obj)
    assert config.default.a == 1
    assert config.b == 2

    config = await Config.a_load_one(dict_obj)
    assert config.default.a == 1
    assert config.b == 2

    with pytest.warns(UserWarning):
        config = await Config.a_load({"a": {"b": 2}}, ini_file)
    assert config.a == 1
    assert config.b == 2

    config = await Config.a_load_one(ini_file_rc, loader="toml")
    assert config.DEFAULT.a == 7
    assert config.TEST.a == 9

    config = await Config.a_load(ini_file_rc, loader="toml")
    assert config.DEFAULT.a == 7
    assert config.TEST.a == 9

    config = await ProfileConfig.a_load(ini_file_rc, loader="toml")
    assert config.a == 7
    assert config.b == 8


def test_nonprofile_file_handler(ini_file_noprofile):
    with open(ini_file_noprofile) as f:
        config = Config.load(f, loader="ini")

    assert config.a == 10
    assert config.h is None


async def test_async_nonprofile_file_handler(ini_file_noprofile):
    ini_file_noprofile = PanPath(ini_file_noprofile)
    async with ini_file_noprofile.a_open() as f:
        config = await Config.a_load(f, loader="ini")

    assert config.a == 10
    assert config.h is None


async def test_wrong_number_of_loaders(toml_file):
    with pytest.raises(ValueError):
        Config.load(toml_file, loader=["toml", "yaml"])

    with pytest.raises(ValueError):
        await Config.a_load(toml_file, loader=["toml", "yaml"])

    with pytest.raises(ValueError):
        ProfileConfig.load(toml_file, loader=["toml", "yaml"])

    with pytest.raises(ValueError):
        await ProfileConfig.a_load(toml_file, loader=["toml", "yaml"])


def test_nonexistent_base_profile(ini_file, ini_file_nodefault):
    with pytest.raises(ValueError):
        ProfileConfig.load(ini_file, base="nonexist")

    # but it is okay when allow_missing_base is True
    config = ProfileConfig.load(ini_file, base="nonexist", allow_missing_base=True)
    config = ProfileConfig.use_profile(config, "default")
    assert config.a == 1
    assert config.b == 2

    with pytest.raises(ValueError):
        ProfileConfig.load(ini_file_nodefault, base="nonexist")

    # but it is okay when allow_missing_base is True
    config = ProfileConfig.load(
        ini_file_nodefault, base="nonexist", allow_missing_base=True
    )
    assert "a" not in config
    assert "b" not in config

    with pytest.raises(ValueError):
        ProfileConfig.load_one(ini_file_nodefault, base="nonexist")

    # but it is okay when allow_missing_base is True
    config = ProfileConfig.load_one(
        ini_file_nodefault, base="nonexist", allow_missing_base=True
    )
    ProfileConfig.use_profile(config, "test", base=None)
    assert config.a == 6


async def test_async_nonexistent_base_profile(ini_file, ini_file_nodefault):
    with pytest.raises(ValueError):
        await ProfileConfig.a_load(ini_file, base="nonexist")

    # but it is okay when allow_missing_base is True
    config = await ProfileConfig.a_load(
        ini_file, base="nonexist", allow_missing_base=True
    )
    config = ProfileConfig.use_profile(config, "default")
    assert config.a == 1
    assert config.b == 2

    with pytest.raises(ValueError):
        await ProfileConfig.a_load(ini_file_nodefault, base="nonexist")

    # but it is okay when allow_missing_base is True
    config = await ProfileConfig.a_load(
        ini_file_nodefault, base="nonexist", allow_missing_base=True
    )
    assert "a" not in config
    assert "b" not in config

    with pytest.raises(ValueError):
        await ProfileConfig.a_load_one(ini_file_nodefault, base="nonexist")

    # but it is okay when allow_missing_base is True
    config = await ProfileConfig.a_load_one(
        ini_file_nodefault, base="nonexist", allow_missing_base=True
    )
    ProfileConfig.use_profile(config, "test", base=None)
    assert config.a == 6


async def test_no_loader_for_stream(toml_file):
    toml_file = PanPath(toml_file)
    with pytest.raises(ValueError):
        with open(toml_file) as f:
            Config.load(f)

    with pytest.raises(ValueError):
        async with toml_file.a_open() as f:
            await Config.a_load(f)

    with pytest.raises(ValueError):
        async with toml_file.a_open() as f:
            await Config.a_load_one(f)

    with pytest.raises(ValueError):
        with open(toml_file) as f:
            ProfileConfig.load(f)

    with pytest.raises(ValueError):
        with open(toml_file) as f:
            ProfileConfig.load_one(f)

    with pytest.raises(ValueError):
        async with toml_file.a_open() as f:
            await ProfileConfig.a_load(f)

    with pytest.raises(ValueError):
        async with toml_file.a_open() as f:
            await ProfileConfig.a_load_one(f)


def test_profile(ini_file, ini_file_rc, ini_file_nodefault):
    config = ProfileConfig.load(ini_file, ini_file_nodefault)

    assert ProfileConfig.current_profile(config) == "default"
    assert ProfileConfig.base_profile(config) == "default"
    assert ProfileConfig.has_profile(config, "default")
    assert ProfileConfig.profiles(config) == ["default", "test"]
    assert ProfileConfig.pool(config) == {
        "default": {"a": 1, "b": 2},
        "test": {"a": 6},
    }
    assert config.a == 1
    assert config.b == 2

    newconf = ProfileConfig.use_profile(config, "test", copy=True)
    assert newconf is not config
    assert ProfileConfig.current_profile(config) == "default"
    assert ProfileConfig.base_profile(config) == "default"
    assert config.a == 1
    assert config.b == 2
    assert ProfileConfig.current_profile(newconf) == "test"
    assert ProfileConfig.base_profile(newconf) == "default"
    assert newconf.a == 6
    assert newconf.b == 2

    ProfileConfig.use_profile(config, "test")
    assert ProfileConfig.current_profile(config) == "test"
    assert ProfileConfig.base_profile(config) == "default"
    assert config.a == 6
    assert config.b == 2

    ProfileConfig.use_profile(config, "default")
    oldconf = config.copy()
    with ProfileConfig.with_profile(config, "test") as newconf:
        assert newconf is config
        assert ProfileConfig.current_profile(newconf) == "test"
        assert ProfileConfig.base_profile(newconf) == "default"
        assert newconf.a == 6
        assert newconf.b == 2
    assert config == oldconf

    config = ProfileConfig.load_one(ini_file_rc)
    assert config.a == "7"

    config = ProfileConfig.load_one(ini_file_rc, loader="toml")
    assert config.a == 7


async def test_async_profile(ini_file, ini_file_rc, ini_file_nodefault):
    config = await ProfileConfig.a_load(ini_file, ini_file_nodefault)

    assert ProfileConfig.current_profile(config) == "default"
    assert ProfileConfig.base_profile(config) == "default"
    assert ProfileConfig.has_profile(config, "default")
    assert ProfileConfig.profiles(config) == ["default", "test"]
    assert ProfileConfig.pool(config) == {
        "default": {"a": 1, "b": 2},
        "test": {"a": 6},
    }
    assert config.a == 1
    assert config.b == 2

    newconf = ProfileConfig.use_profile(config, "test", copy=True)
    assert newconf is not config
    assert ProfileConfig.current_profile(config) == "default"
    assert ProfileConfig.base_profile(config) == "default"
    assert config.a == 1
    assert config.b == 2
    assert ProfileConfig.current_profile(newconf) == "test"
    assert ProfileConfig.base_profile(newconf) == "default"
    assert newconf.a == 6
    assert newconf.b == 2

    ProfileConfig.use_profile(config, "test")
    assert ProfileConfig.current_profile(config) == "test"
    assert ProfileConfig.base_profile(config) == "default"
    assert config.a == 6
    assert config.b == 2

    ProfileConfig.use_profile(config, "default")
    oldconf = config.copy()
    with ProfileConfig.with_profile(config, "test") as newconf:
        assert newconf is config
        assert ProfileConfig.current_profile(newconf) == "test"
        assert ProfileConfig.base_profile(newconf) == "default"
        assert newconf.a == 6
        assert newconf.b == 2
    assert config == oldconf

    config = await ProfileConfig.a_load_one(ini_file_rc)
    assert config.a == "7"

    config = await ProfileConfig.a_load_one(ini_file_rc, loader="toml")
    assert config.a == 7


def test_use_profile_base_none():
    config = ProfileConfig.load(
        {"default": {"a": 1, "b": 2}, "p1": {"a": 6}, "p2": {"a": 7}}
    )
    ProfileConfig.use_profile(config, "p1", None)
    assert config.a == 6
    assert "b" not in config

    ProfileConfig.use_profile(config, "default")
    conf2 = ProfileConfig.use_profile(config, "p2", None, copy=True)
    assert conf2.a == 7
    assert "b" not in conf2

    assert config.a == 1
    assert config.b == 2


def test_use_profile_base_not_existing():
    config = ProfileConfig.load(
        {"default": {"a": 1, "b": 2}, "p1": {"a": 6}, "p2": {"a": 7}}
    )
    ProfileConfig.use_profile(config, "p1", "x", allow_missing_base=True)
    assert config.a == 6
    assert "b" not in config

    with pytest.raises(ValueError):
        ProfileConfig.use_profile(config, "p2", "x", allow_missing_base=False)


def test_detach():
    config = ProfileConfig.load({"default": {"a": 1, "b": [2, 3]}, "p1": {"a": 6}})
    ProfileConfig.use_profile(config, "p1")
    diot = ProfileConfig.detach(config)
    assert diot.a == 6
    assert diot.b == [2, 3]
    assert len(diot) == 2
    diot.b[0] = 10
    assert config.b == [2, 3]


def test_loader_directive_liq(toml_with_liq_directive):
    """First-line '# simpleconf-loader: liq' redirects to the liq loader."""
    config = Config.load(toml_with_liq_directive)
    assert config.default.a == 2
    assert config.default.b == 12


def test_loader_directive_liquid(yaml_with_liquid_directive):
    """First-line '# simpleconf-loader: liquid' redirects to the liq loader."""
    config = Config.load(yaml_with_liquid_directive)
    assert config.default.a == 2
    assert config.b == 6


def test_loader_directive_explicit(toml_with_explicit_liq_directive):
    """First-line '# simpleconf-loader: toml.liq' redirects explicitly."""
    config = Config.load(toml_with_explicit_liq_directive)
    assert config.default.a == 2
    assert config.default.b == 12


async def test_async_loader_directive(toml_with_liq_directive):
    """Async loading also honours the first-line directive."""
    config = await Config.a_load(toml_with_liq_directive)
    assert config.default.a == 2
    assert config.default.b == 12


def test_profile_loader_directive_liq(toml_profile_with_liq_directive):
    """ProfileConfig.load also honours the first-line directive."""
    config = ProfileConfig.load(toml_profile_with_liq_directive)
    assert config.a == 2
    assert config.b == 12


# --- loadenv directive tests ---


def test_config_load_with_loadenv(yaml_with_loadenv):
    """$env:VAR references resolve from .env file."""
    config = Config.load(yaml_with_loadenv)
    assert config.db.host == "localhost"
    assert config.db.port == 5432  # @int:5432 cast to int


def test_config_load_with_loadenv_custom_path(yaml_with_loadenv_custom):
    """Custom .env path via directive."""
    config = Config.load(yaml_with_loadenv_custom)
    assert config.custom == "custom_value"


def test_config_load_with_loadenv_fallback_osenv(yaml_with_loadenv_osenv_fallback):
    """Fall back to os.environ when var not in .env file."""
    import os
    config = Config.load(yaml_with_loadenv_osenv_fallback)
    assert config.path == os.environ.get("PATH", "")


def test_config_load_with_loadenv_and_loader(yaml_with_loadenv_and_loader):
    """Both loadenv and loader directives work together."""
    config = Config.load(yaml_with_loadenv_and_loader)
    assert config.db.host == "localhost"
    assert config.db.port == 5432  # @int:5432 cast to int
    assert config.db2.host == "localhost"
    assert config.db2.port == 5432


def test_config_load_with_loadenv_ini(ini_with_loadenv):
    """$env:VAR references work in INI configs."""
    config = Config.load(ini_with_loadenv)
    assert config.host == "localhost"
    assert config.port == 5432  # port: @int:5432


def test_config_load_with_loadenv_toml(toml_with_loadenv):
    """$env:VAR references work in TOML configs."""
    config = Config.load(toml_with_loadenv)
    assert config.default.host == "localhost"
    assert config.default.port == 5432  # @int:5432 cast to int


def test_loadenv_required_raises(tmp_path):
    """$env:NONEXISTENT without modifier raises ValueError by default."""
    env = tmp_path / ".env"
    env.write_text("A=1\n")
    f = tmp_path / "config.yaml"
    f.write_text(
        "# simpleconf-loadenv\n"
        "a: $env:A\n"
        "b: $env:NONEXISTENT\n"
    )
    with pytest.raises(ValueError, match="NONEXISTENT"):
        Config.load(f)


def test_loadenv_required_raises_explicit(tmp_path):
    """$env:NONEXISTENT:required raises ValueError."""
    env = tmp_path / ".env"
    env.write_text("A=1\n")
    f = tmp_path / "config.yaml"
    f.write_text(
        "# simpleconf-loadenv\n"
        "b: $env:NONEXISTENT:required\n"
    )
    with pytest.raises(ValueError, match="NONEXISTENT"):
        Config.load(f)


def test_loadenv_optional_asis_not_found(tmp_path):
    """$env:NONEXISTENT:optional-asis keeps the $env: reference as-is."""
    env = tmp_path / ".env"
    env.write_text("A=1\n")
    f = tmp_path / "config.yaml"
    f.write_text(
        "# simpleconf-loadenv\n"
        "a: $env:A:optional-asis\n"
        "b: $env:NONEXISTENT:optional-asis\n"
    )
    config = Config.load(f)
    assert config.a == "1"
    assert config.b == "$env:NONEXISTENT"


def test_loadenv_optional_empty_not_found(tmp_path):
    """$env:NONEXISTENT:optional-empty resolves to empty string."""
    env = tmp_path / ".env"
    env.write_text("A=1\n")
    f = tmp_path / "config.yaml"
    f.write_text(
        "# simpleconf-loadenv\n"
        "a: $env:A:optional-empty\n"
        "b: $env:NONEXISTENT:optional-empty\n"
    )
    config = Config.load(f)
    assert config.a == "1"
    assert config.b == ""


def test_loadenv_unknown_modifier_falls_back_to_required(tmp_path):
    """Unknown modifier is treated as part of the var name."""
    f = tmp_path / "config.yaml"
    f.write_text(
        "# simpleconf-loadenv\n"
        "b: $env:NONEXISTENT:unknown\n"
    )
    with pytest.raises(ValueError, match="NONEXISTENT:unknown"):
        Config.load(f)
