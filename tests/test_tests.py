import configparser
import pathlib

import yaml


def _load_ci_conf():
    return yaml.safe_load(
        pathlib.Path(".github/workflows/ci.yaml").read_text()
    )


def _load_tox_conf():
    config = configparser.ConfigParser()
    config.read(pathlib.Path("tox.ini"))
    return {section: dict(contents) for section, contents in config.items()}


def test_tox_commands_match_ci_commands():
    ci_conf = _load_ci_conf()
    ci_commands = set()
    for job in ci_conf["jobs"].values():
        if job["name"] == "Coverage":
            continue
        step = job["steps"][-1]
        command = step["run"].strip()
        ci_commands.add(command)

    tox_conf = _load_tox_conf()
    tox_commands = set()
    for section, contents in tox_conf.items():
        if not section.startswith("testenv"):
            continue
        command = contents["commands"].strip()
        tox_commands.add(command)

    assert ci_commands == tox_commands


def test_tox_python_versions_match_ci_python_versions():
    ci_conf = _load_ci_conf()
    ci_matrix = ci_conf["jobs"]["unittests"]["strategy"]["matrix"]
    ci_versions = set(ci_matrix["python-version"])

    tox_conf = _load_tox_conf()
    tox_versions = {
        f"3.{env[3:]}"
        for env in tox_conf["tox"]["envlist"].strip().split(",")
        if env.startswith("py3")
    }

    assert ci_versions == tox_versions
