import json
import shutil
import sys
import os

from typing import List
from utils.LogUtil import LogUtil
from ast import Delete
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

class FileUtil():
    def __init__(self) -> None:
        self.log_util = LogUtil(__name__)

    def write_file(self, file_path: List[str], content: str) -> None:
        self.log_util.record_info("write content in file")
        file_name, file_extension = os.path.splitext(file_path)
        with open(file_path, "w", encoding = 'utf-8') as f:
            if file_extension == '.txt':
                content = str(content)
                f.write(content) 
            elif file_extension == '.json':
                f.write(json.dumps(content))

    def delete_file(self, file_path: List[str]) -> None:
        self.log_util.record_info("delete file or folder")
        if os.path.isfile(file_path):
            os.remove(file_path)
        else:
            shutil.rmtree(file_path)

    def read_file(self, file_path: List[str]) -> None:
        with open(file_path, 'w') as f:
            content = f.read()
            
        return content