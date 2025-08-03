import tomli
import tomli_w


def load_toml_data(toml_path: str) -> dict:
    with open(toml_path, "rb") as toml_file:
        toml_data: dict = tomli.load(toml_file)
    return toml_data


def save_toml_data(toml_path: str, toml_data: dict) -> None:
    with open(toml_path, "wb") as toml_file:  # Use "wb" for binary write
        tomli_w.dump(toml_data, toml_file)
