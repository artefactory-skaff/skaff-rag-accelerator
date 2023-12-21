import os
from pathlib import Path

import yaml
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader


def get_config(config_file_path: Path) -> dict:
    load_dotenv()
    env = Environment(loader=FileSystemLoader(config_file_path))
    template = env.get_template("config.yaml")
    config = template.render(os.environ)
    return yaml.safe_load(config)
