import pytest


@pytest.fixture(scope="module")
def config_path(tmp_path_factory):
    # one tmp path for this module
    return tmp_path_factory.mktemp("configs")


@pytest.fixture(scope="module")
def ini_file(config_path):
    ret = config_path / 'default.ini'
    ret.write_text("""[default]
a = @int:1
b = @int:2

[TEST]
a = @int:3
""")
    return ret


@pytest.fixture(scope="module")
def ini_file_nodefault(config_path):
    ret = config_path / 'default_upper.ini'
    ret.write_text("""[TEST]
a = @int:6
""")
    return ret


@pytest.fixture(scope="module")
def ini_file_rc(config_path):
    ret = config_path / '.pylintrc'
    ret.write_text("""[DEFAULT]
a = 7
b = 8

[TEST]
a = 9
""")
    return ret


@pytest.fixture(scope="module")
def ini_file_noprofile(config_path):
    ret = config_path / 'noprofile.ini'
    ret.write_text("""[DEFAULT]
a = @py:10
b = 11
c = x:y
d = @int:12
e = @float:13.1
f = @bool:true
g = csv:a,b,c
h = @none
i = @float:1e-3
j = true
k = k
""")
    return ret


@pytest.fixture(scope="module")
def ini_j2_file_nondefault(config_path):
    ret = config_path / 'default.j2.ini'
    ret.write_text("""[default]
a = @int:{{ 1 + 1 }}
b = @int:{{ 2 + 2 }}
""")
    return ret


@pytest.fixture(scope="module")
def env_file(config_path):
    ret = config_path / 'env.env'
    ret.write_text("""
default_a=@int:1
b=@int:2
""")
    return ret


@pytest.fixture(scope="module")
def yaml_file(config_path):
    ret = config_path / 'simpleconf.yaml'
    ret.write_text("""default:
  a: 1
b: 2
""")
    return ret


@pytest.fixture(scope="module")
def yaml_j2_file(config_path):
    ret = config_path / 'simpleconf.j2.yaml'
    ret.write_text("""default:
  a: {{ 1 + 1 }}
b: {{ 2 + 2 }}
""")
    return ret


@pytest.fixture(scope="module")
def json_file(config_path):
    ret = config_path / 'simpleconf.json'
    ret.write_text("""{"default": {"a": 1}, "b": 2}
""")
    return ret


@pytest.fixture(scope="module")
def json_liq_file(config_path):
    ret = config_path / 'simpleconf.json.liq'
    ret.write_text("""{
  "default": {
    "a": {{ 1 + 1 }}
  }
}
""")
    return ret


@pytest.fixture(scope="module")
def toml_file(config_path):
    ret = config_path / 'simpleconf.toml'
    ret.write_text("""b = 2
[default]
a = 1
""")
    return ret


@pytest.fixture(scope="module")
def toml_liq_file(config_path):
    ret = config_path / 'simpleconf.toml.liq'
    ret.write_text("""b = 2

{% set x = 10 %}
[default]
a = {{ 1 + 1 }}
b = {{ x + 2 }}
""")
    return ret


@pytest.fixture(scope="module")
def toml_with_liq_directive(config_path):
    ret = config_path / 'directive_liq.toml'
    ret.write_text(
        "# simpleconf-loader: liq\n"
        "b = 2\n"
        "\n"
        "{% set x = 10 %}\n"
        "[default]\n"
        "a = {{ 1 + 1 }}\n"
        "b = {{ x + 2 }}\n"
    )
    return ret


@pytest.fixture(scope="module")
def toml_profile_with_liq_directive(config_path):
    ret = config_path / 'directive_liq_profile.toml'
    ret.write_text(
        "# simpleconf-loader: liq\n"
        "\n"
        "{% set x = 10 %}\n"
        "[default]\n"
        "a = {{ 1 + 1 }}\n"
        "b = {{ x + 2 }}\n"
    )
    return ret


@pytest.fixture(scope="module")
def yaml_with_liquid_directive(config_path):
    ret = config_path / 'directive_liquid.yaml'
    ret.write_text(
        "# simpleconf-loader: liquid\n"
        "{% set x = 5 %}\n"
        "default:\n"
        "  a: {{ 1 + 1 }}\n"
        "b: {{ x + 1 }}\n"
    )
    return ret


@pytest.fixture(scope="module")
def toml_with_explicit_liq_directive(config_path):
    ret = config_path / 'directive_explicit.toml'
    ret.write_text(
        "# simpleconf-loader: toml.liq\n"
        "b = 2\n"
        "\n"
        "{% set x = 10 %}\n"
        "[default]\n"
        "a = {{ 1 + 1 }}\n"
        "b = {{ x + 2 }}\n"
    )
    return ret


@pytest.fixture(scope="module")
def dict_obj():
    return {"default": {"a": 1}, "b": 2}


@pytest.fixture(scope="module")
def dotenv_file(config_path):
    """A .env file with some test vars."""
    ret = config_path / ".env"
    ret.write_text("DB_HOST=localhost\nDB_PORT=@int:5432\n")
    return ret


@pytest.fixture(scope="module")
def yaml_with_loadenv(config_path, dotenv_file):
    """YAML config with loadenv directive (default path)."""
    ret = config_path / "loadenv_test.yaml"
    ret.write_text(
        "# simpleconf-loadenv\n"
        "db:\n"
        "  host: $env:DB_HOST\n"
        "  port: $env:DB_PORT\n"
    )
    return ret


@pytest.fixture(scope="module")
def yaml_with_loadenv_custom(config_path):
    """YAML config with loadenv directive (custom path)."""
    # Create .env in a subdirectory
    sub = config_path / "sub"
    sub.mkdir(exist_ok=True)
    env_file = sub / "custom.env"
    env_file.write_text("CUSTOM_VAR=custom_value\n")
    ret = config_path / "loadenv_custom.yaml"
    ret.write_text(
        f"# simpleconf-loadenv: {env_file}\n"
        "custom: $env:CUSTOM_VAR\n"
    )
    return ret


@pytest.fixture(scope="module")
def yaml_with_loadenv_and_loader(config_path, dotenv_file):
    """YAML config with both loadenv and loader directives."""
    ret = config_path / "loadenv_loader.yaml"
    ret.write_text(
        "# simpleconf-loadenv\n"
        "# simpleconf-loader: liq\n"
        "db:\n"
        "  host: $env:DB_HOST\n"
        "  port: $env:DB_PORT\n"
        "db2:\n"
        "  host: {{ env.DB_HOST }}\n"
        "  port: {{ env.DB_PORT }}\n"
    )
    return ret


@pytest.fixture(scope="module")
def yaml_with_loadenv_osenv_fallback(config_path):
    """YAML config with loadenv and os.environ fallback."""
    ret = config_path / "loadenv_fallback.yaml"
    ret.write_text(
        "# simpleconf-loadenv\n"
        "path: $env:PATH\n"
    )
    return ret


@pytest.fixture(scope="module")
def ini_with_loadenv(config_path, dotenv_file):
    """INI config with loadenv directive."""
    ret = config_path / "loadenv_test.ini"
    ret.write_text(
        "# simpleconf-loadenv\n"
        "[default]\n"
        "host = $env:DB_HOST\n"
        "port = $env:DB_PORT\n"
    )
    return ret


@pytest.fixture(scope="module")
def toml_with_loadenv(config_path, dotenv_file):
    """TOML config with loadenv directive."""
    ret = config_path / "loadenv_test.toml"
    ret.write_text(
        "# simpleconf-loadenv\n"
        "[default]\n"
        "host = \"$env:DB_HOST\"\n"
        "port = \"$env:DB_PORT\"\n"
    )
    return ret
