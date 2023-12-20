import os
from pathlib import Path

import yaml
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader


def get_config() -> dict:
    load_dotenv()
    env = Environment(loader=FileSystemLoader(Path(__file__).parent))
    template = env.get_template("config.yaml")
    config = template.render(os.environ)
    return yaml.safe_load(config)


def load_models_config():
    with open(Path(__file__).parent / "config.yaml", "r") as file:
        return yaml.safe_load(file)


if __name__ == "__main__":
    print(get_config())
