import json
from pathlib import Path
from typing import List, Dict, Optional, Union

class FileManager:
    def __init__(self, base_path: Union[str, Path] = None):
        self.base_path = Path(base_path) if base_path else Path(__file__).parent.parent
        self.data_path = self.base_path / "data"
        self.dungeons_path = self.data_path / "dungeons"
        self.npcs_path = self.data_path / "npcs"
        self.saves_path = self.base_path / "saves"
        self._ensure_directories()

    def _ensure_directories(self):
        for path in [self.data_path, self.dungeons_path, self.npcs_path, self.saves_path]:
            path.mkdir(parents=True, exist_ok=True)

    def list_files(self, directory: str, extension: str = None) -> List[str]:
        path = self.base_path / directory
        try:
            return [
                f.name for f in path.iterdir() 
                if f.is_file() and (not extension or f.suffix == extension)
            ]
        except Exception as e:
            print(f"[Error] Failed to list files: {e}")
            return []

    def list_dungeon_files(self) -> List[str]:
        return self.list_files(self.dungeons_path.relative_to(self.base_path), '.json')

    def read_json(self, filename: str) -> Optional[Dict]:
        path = self.dungeons_path / filename
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[Error] Failed to read {path}: {e}")
            return None

    def write_json(self, filename: str, data: Dict) -> bool:
        path = self.dungeons_path / filename
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"[Error] Failed to write {path}: {e}")
            return False