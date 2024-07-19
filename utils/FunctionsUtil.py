import sys
import os
import re
import json

from typing import Dict, List, Tuple
from pathlib import Path
from collections import defaultdict

from utils.LogUtil import LogUtil

sys.path.append(str(Path(__file__).resolve().parent.parent))

class FunctionsUtil():
    def __init__(self) -> None:
        self.log_util = LogUtil(__name__)

    def split_title(self, content: str) -> Tuple[str, str]:
        self.log_util.record_info("split title and content")
        temp = content.split("</h1>")
        title = temp[0].split("<h1>")
        
        return title[1], temp[1]

    def split_select_image(self, assistant_result: str) -> List[str]:
        self.log_util.record_info("split selected image from assistant")
        selected_image = []
        for image in assistant_result.split(','):
            selected_image.append(image)

        return selected_image

    def replace_content_img(self, images: List[str], content: str) -> str:
        self.log_util.record_info("replace content img tag")
        content = json.loads(content)
        result = ""
        i = 0
        for c in content:
            for paragraph in c:
                if "content" in paragraph:
                    text = paragraph["content"]
                    while "**" in text:
                        text.replace("**", "<strong>")
                        text.replace("**", "</strong>")
                    result += f'<{paragraph["tag"]}>{text}</{paragraph["tag"]}>'
                    
                if paragraph["tag"] == "img":
                    result += f'<img src="{images[i]}">'
                    i += 1
                
        return result
    
    def clear_console(self) -> None:
        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')

    def extract(self,scores_list: List[Dict[int, List]]) -> Dict[int, List]:
        result = {}
        for paragraph_index, scores in enumerate(scores_list, start=1):
            self.log_util.record_info(f"Extracting target images for paragraph {paragraph_index}")
            paragraph_result = []
            keys = sorted(scores.keys(), reverse=True)
            index = 0
            
            while keys and index < 10:
                key = keys.pop(0)
                for value in scores[key]:
                    if index < 10:
                        paragraph_result.append(value)
                        index += 1
                    else:
                        break
            
            result[paragraph_index] = paragraph_result

        return result
    
    def split_paragraph(self, content: str) -> str:
        # 正則表達式匹配HTML標籤及其內容
        pattern = re.compile(r'(<\w+>)(.*?)(</\w+>)', re.DOTALL)

        # 解析內文
        matches = pattern.findall(content)
        parsed_content = [{"tag": match[0], "content": match[1].strip()} for match in matches]

        # 輸出成JSON格式
        result = json.dumps(parsed_content, ensure_ascii=False, indent=4)
        
        return result
    
    def validate_input(self, input_data: str) -> bool:
        try:
            data = json.loads(input_data)
        except ValueError:
            return False

        if not isinstance(data, list):
            return False

        for item in data:
            if not isinstance(item, list):
                return False

            for obj in item:
                if not isinstance(obj, dict):
                    return False

                if "tag" not in obj or "content" not in obj:
                    return False

                tag = obj["tag"]
                content = obj["content"]

                if not isinstance(tag, str) or not isinstance(content, str):
                    return False

        return True