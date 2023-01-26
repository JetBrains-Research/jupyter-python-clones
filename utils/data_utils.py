import zipfile
import pandas as pd
import json
from pathlib import Path


def unzip_data(base_path: Path | str = Path("data/in/")):
    if isinstance(base_path, str):
        base_path = Path(base_path)

    for archive in base_path.glob("*.zip"):
        with zipfile.ZipFile(archive, 'r') as zip_ref:
            zip_ref.extractall(base_path)


def input_data_to_df(base_path: Path):
    data = []
    for path in base_path.rglob('*.py'):
        with open(path, 'r') as f:
            data.append({'name': path.name, 'content': f.read()})

    return pd.DataFrame(data)


def output_data_to_df(base_path: Path):
    data = []
    for path in base_path.rglob('*.json'):
        try:
            with open(path, 'r') as f:
                d = json.loads(json.load(f).get('3'))
                d['name'] = path.name
                data.append(d)

        except TypeError:
            print(f"ERROR WITH OPEN {path}")
            continue

    return pd.json_normalize(data, max_level=1)


if __name__ == "__main__":
    # unzip_data("data/in/")
    # unzip_data("data/out/")

    df_in = output_data_to_df(Path('data/in/notebooks_1k'))
    df_out = output_data_to_df(Path('data/out/notebooks_1k'))
