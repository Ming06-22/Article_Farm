# -*- coding: utf-8 -*-

import os
import threading
import requests
import json
import base64
import time

from typing import Dict, List
from threading import Thread
from collections import defaultdict
from alive_progress import alive_bar

from utils.YamlUtil import YamlUtil
from utils.LogUtil import LogUtil

class AnalyzeImageService(Thread):
    def __init__(self, yaml: YamlUtil) -> None:
        threading.Thread.__init__(self)
        self.gemini_key = yaml.get_value("ai_key", "gemini")
        self.scores = []
        self.log_util = LogUtil(__name__)

    def evaluate(self, summary: str, images: List[str], paragraph: int,gemini_key: str, bar: alive_bar) -> None:
        self.log_util.record_info("evaluate images")
        templist = defaultdict(list)
        for img in images:
            try:
                img = "./resources/img/" + img
                with open(img, "rb") as image_file:
                    image_base64_string = base64.b64encode(image_file.read()).decode('utf-8')

                url = f'https://generativelanguage.googleapis.com/v1/models/gemini-pro-vision:generateContent?key={gemini_key}'
                headers = {'Content-Type': 'application/json'}
                data = {
                    "contents": [
                        {
                            "parts": [
                                {"text": f"請根據以下文章以及提供的圖像，為兩者的關聯性打分。關聯性越高則分數越高，關聯性越低則分數越低。最低分0分、最高分100分。回答的結果請在第一行簡答分數。\n{summary}"},
                                {
                                    "inline_data": {
                                        "mime_type": "image/jpeg",
                                        "data": image_base64_string
                                    }
                                }
                            ]
                        },
                    ]
                }
                response = requests.post(url, headers=headers, json=data)
                response = json.loads(response.text)["candidates"][0]["content"]["parts"][0]["text"]
                
                temp = response.split("\n")[0]
                score = ""
                while temp and not temp[0].isnumeric():
                    temp = temp[1: ]
                while temp and temp[0].isnumeric():
                    score += temp[0]
                    temp = temp[1: ]
                
                templist[int(score)].append((img, response))

            except:
                pass
            finally:
                bar()
                
        while len(self.scores) < paragraph:
            self.scores.append([])
        self.scores[paragraph-1] = templist

    def thread_evaluate(self, summary: str) -> Dict[int, tuple[str, str]]:
        # 獲取當前檔案的目錄
        code_dir = os.path.dirname(os.path.abspath(__file__))
        # 構建相對路徑
        img_dir = os.path.join(code_dir,'..', "resources", "img")    
        
        folder = os.listdir(img_dir)
        images = defaultdict(list)

        for f in folder:
            paragraph = f.split("_")[0]
            images[int(paragraph)].append(f)

        self.score = [[] for _ in range(len(images))]
        threads = []
        with alive_bar(len(folder)) as bar:
            for i, image in images.items():
                thread = threading.Thread(target=self.evaluate, args=(summary, image, i, self.gemini_key[i%5], bar))
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join()

        return self.scores