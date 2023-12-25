import os
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader


def get_config(config_file_path: Path) -> dict:
    env = Environment(loader=FileSystemLoader(config_file_path))
    template = env.get_template("config.yaml")
    config = template.render(os.environ)
    return yaml.safe_load(config)
