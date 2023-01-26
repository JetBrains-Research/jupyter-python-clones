import json
import pandas as pd

from pathlib import Path
from typing import Dict, List
from tqdm import tqdm


class Experiment:
    def __init__(self, notebooks_folder, scripts_folder=None, max_num=50, in_path=None):
        self.notebooks_folder = notebooks_folder
        self.scripts_folder = scripts_folder
        self.max_num = max_num

        self.files = self._get_files()
        self.in_path = in_path
        self.source_files = self._get_source_files() if in_path else {'notebooks': [], 'scripts': []}

        self.length_range = None
        self.aggregated_stats = {'notebooks': None, 'scripts': None}

        self.cell_separator = "\n# [___CELL_SEPARATOR___]\n"

    def _get_json_files(self, folder: Path) -> List[Path]:
        return [json_path for json_path in folder.rglob("*.json")][:self.max_num]

    @staticmethod
    def __get_source_path(name: Path, in_folder: Path) -> Path:
        return in_folder / Path(str(name).split("/")[-1].replace("#", '/')[:-5])

    def _get_source_files(self) -> Dict[str, List[Path]]:
        return {k: [self.__get_source_path(file, in_folder=folder) for file in self.files[k]]
                for k, folder in self.in_path.items()}

    def _get_files(self) -> Dict[str, List[Path]]:
        notebook_files = None if not self.notebooks_folder else self._get_json_files(self.notebooks_folder)
        scripts_files = None if not self.scripts_folder else self._get_json_files(self.scripts_folder)

        files = {'notebooks': notebook_files, 'scripts': scripts_files}
        return files

    @staticmethod
    def read_clones_data(filepath: Path) -> Dict | None:
        first_level_key = "3"

        with filepath.open('r') as f:
            clones_dict = json.load(f)

        if first_level_key not in clones_dict:
            return None
        else:
            clones_dict[first_level_key] = json.loads(clones_dict[first_level_key])
            return clones_dict

    def filter_clones(self, data: Dict, min_length: int = 10, max_length: int = 10_000, breaks: bool = False,
                      source_path: Path = None) -> List[Dict]:
        lst = list(filter(
            lambda f: min_length <= f["clone_length"] <= max_length,
            data["3"]["groups"]
        ))
        if breaks:
            for i, g in enumerate(lst):
                lst[i]['clones'] = self.filter_breaks(g['clones'], source_path)

        return lst

    @staticmethod
    def get_stats(lst: List, norm: int = 1) -> Dict:
        return {
            'groups_cnt': len(lst) / norm,
            'clones_cnt': sum([len(g["clones"]) for g in lst]) / norm
        }

    def is_break(self, start: int, finish: int, source: str) -> bool:
        return self.cell_separator in source[start:finish]

    def filter_breaks(self, clones, source_path: Path) -> List[Dict]:
        with source_path.open('r') as f:
            source = f.read()
        return [clone for clone in clones
                if not self.is_break(*clone['position'], source=source)]

    def _aggregate(self, files, length_range, source_paths, normalize=False, drop_breaks=False) -> pd.DataFrame:
        stats = []

        for i, file in tqdm(enumerate(files)):
            data_tmp = self.read_clones_data(file)
            if data_tmp is None:
                continue

            norm = data_tmp.get('initial_tree_length') if normalize else 1
            path = source_paths[i] if source_paths else None
            drop_breaks = drop_breaks if path else None

            stats_tmp = []
            for min_l in length_range:
                filtered_clones = self.filter_clones(data=data_tmp, min_length=min_l,
                                                     breaks=drop_breaks, source_path=path)
                clones_stats = self.get_stats(filtered_clones, norm=norm)
                stats_tmp.append(clones_stats)

            stats_tmp = pd.DataFrame(stats_tmp)
            stats_tmp['min_length'] = list(length_range)

            stats.append(pd.DataFrame(stats_tmp))

        stats = pd.concat(stats)
        return stats

    def run(self, length_range=range(3, 91), normalize=False, drop_breaks=False):
        self.length_range = length_range
        for files_type, files in self.files.items():
            if files is not None:
                self.aggregated_stats[files_type] = self._aggregate(
                    files, length_range, self.source_files.get(files_type),
                    normalize=normalize, drop_breaks=drop_breaks
                )


if __name__ == "__main__":
    notebooks_path = Path('../clones-study/data/out/notebooks_1k')
    scripts_path = Path('../clones-study/data/out/scripts_1k')

    e = Experiment(
        notebooks_folder=notebooks_path,
        scripts_folder=scripts_path,
        max_num=1000
    )

    min_clone_length, max_clone_length = 3, 91
    e.run(normalize=False, drop_breaks=False, length_range=range(min_clone_length, max_clone_length))
