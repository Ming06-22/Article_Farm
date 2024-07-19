import yaml
import sys
from pathlib import Path
from typing import Tuple

sys.path.append(str(Path(__file__).resolve().parent.parent))

class YamlUtil():
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        with open(self.file_path, "r",encoding="utf-8") as stream:
            self.file = yaml.safe_load(stream)

    def get_value(self, main_key: str, value_key: str) -> str:
        return self.file[main_key][value_key]

    def get_article_category(self, category: str) -> Tuple[str, str]:
        for temp in self.file['article']:
            if temp['category'] == category:
                return temp['category_id'], temp['prompt']
            
    def get_assistant_function(self, target_function: str) -> Tuple[str, str]:
        for function in self.file['openai']:
            if function['function'] == target_function:
                return function['assistant_id'], function['vector_space_id']
