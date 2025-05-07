import json
from pathlib import Path
from typing import List, Dict, Optional, Union

class FileManager:
    def __init__(self, base_path: Union[str, Path] = None):
        # Determine base project root path
        if base_path:
            root = Path(base_path).resolve()
        else:
            root = Path(__file__).resolve().parent
            while not (root / "data").exists() and root.parent != root:
                root = root.parent
        self.base_path = root

        # Set key directory paths
        self.data_path = self.base_path / "data"
        self.dungeons_path = self.data_path / "dungeons"
        self.npcs_path = self.data_path / "npcs"
        self.classes_path = self.data_path / "Classes" if (self.data_path / "Classes").exists() else self.data_path / "classes"
        self.saves_path = self.base_path / "saves"

        # Ensure all necessary directories exist
        for p in (self.data_path, self.dungeons_path, self.npcs_path, self.classes_path, self.saves_path):
            p.mkdir(parents=True, exist_ok=True)

    def list_files(self, directory: Path, extension: str = None) -> List[str]:
        # List files in a directory, optionally filtered by extension
        try:
            return [f.name for f in directory.iterdir() if f.is_file() and (not extension or f.suffix.lower() == extension.lower())]
        except Exception as e:
            print(f"[Error] Failed to list files in {directory}: {e}")
            return []

    def list_dungeon_files(self) -> List[str]:
        # List all .json files in the dungeons folder
        return self.list_files(self.dungeons_path, ".json")

    def read_json(self, *args) -> Optional[Dict]:
        # Read JSON file from either default (dungeons) or custom directory
        if len(args) == 1:
            directory = self.dungeons_path
            filename = args[0]
        elif len(args) == 2:
            directory, filename = args
        else:
            raise ValueError
        path = directory / filename
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[Error] Failed to read {path}: {e}")
            return None

    def write_json(self, *args) -> bool:
        # Write data as JSON to a file in default or custom directory
        if len(args) == 2:
            directory = self.dungeons_path
            filename, data = args
        elif len(args) == 3:
            directory, filename, data = args
        else:
            raise ValueError
        path = directory / filename
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"[Error] Failed to write {path}: {e}")
            return False