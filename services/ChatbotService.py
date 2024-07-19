# -*- coding: utf-8 -*-

import autogen
import requests
import yaml
import json
import base64
import matplotlib.pyplot as plt
import requests
import os
import sys

from autogen import Agent, AssistantAgent, ConversableAgent, UserProxyAgent
from pathlib import Path
from typing import Dict, List
sys.path.append(str(Path(__file__).resolve().parent.parent))

from utils.LogUtil import LogUtil
from utils.YamlUtil import YamlUtil
from utils.DALLEAgent import DALLEAgent
from openai import OpenAI

class ChatbotService():
    # yaml: YamlUtil, model: str
    def __init__(self, yaml: YamlUtil, model: str) -> None:
        self.log_util = LogUtil(__name__)
        ai_key = yaml.get_value("ai_key", model)

        # config for GPT-4
        self.openai_llm_config = {
            "timeout": 60,
            "temperature": 0,
            "api_key": ai_key,
            "model": "gpt-4o",
        }

        self.dalle_llm_config = autogen.config_list_from_json(
            "./ai_model.json",
            filter_dict = {
                "model": ["dalle"],
            },
        )

        self.dalle_llm_config = autogen.config_list_from_json(
            "./ai_model.json",
            filter_dict = {
                "model": ["dalle"],
            },
        )

    def expand_keyword(self, keyword: str) -> List[str]:
        self.log_util.record_info("found expand keyword")
        agent = AssistantAgent(
            name = "Keyword Robot",
            system_message = "Full of imagination, expert of technology",
            llm_config = self.openai_llm_config,
        )

        reply = agent.generate_reply(messages=[
            {"content": f"Please base on '{keyword}' to generate 10 english keywords and 10 traditional chinese keywords. The keywords must to be a experience sharing, but not store selling. I hope I can use the keywords to search more information on Google.", "role": "user"}])
        reply = reply.split("\n")

        result = []
        for r in reply:
            if r and r[0].isnumeric():
                r = " ".join(r.split(" ")[1:])
                if r[0] in ("'", "\""):
                    r = r[1: -1]
                result.append(r)

        return result
    
    def generate_article_prompt(self, article_content: str) -> str:
        # 根據文章內容產生封面圖片的提示詞。
        prompt = f"請閱讀下面這篇文章,並給我這段文章適合生成封面圖片的prompt,我的圖片中不要有文字: \"{article_content}\""

        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers = {'Authorization': ''},
            json = {
                'model': "gpt-4-turbo",  # 使用新的模型名稱
                'messages': [{"role": "system", "content": prompt}],
                'temperature': 0.7
            }
        )

        response_json = response.json()
    
        # 檢查是否有錯誤返回，並處理錯誤情況
        if 'choices' in response_json and response_json['choices']:
            image_prompt = response_json['choices'][0]['message']['content'].strip()
            
            return image_prompt
        # 處理錯誤或無效響應
        else:
            return "無法生成提示,請檢查API呼叫和輸入。"

    def generate_title_image(self, artical:str ) -> None:
        image_prompt = self.generate_article_prompt(artical)
        image_url, content = self.generate_image(messages={
            "content": f"""ID[file-ShsA6YlnSTxZNUtlIpkFPNmt]依照ID並結合下面的prompt幫我生出一張16:9的圖片
            圖片風格prompt[ 以充滿活力的卡通向量風格描繪。展現出年輕、科技感十足的氛圍。採用動態、扁平的配色方案。圖畫風格為色塊表現，勾勒黑邊。色調以橘色、黃色為主。要包含背景，整體顏色不需太多。]
            圖片內容prompt [{image_prompt}] """, 
            "size": "1792x1024", #16:9
            "quality": "standard"
            })
        if image_url:
            self.download_image(image_url)

    def generate_image(self,messages:Dict) -> None:
        dalle = DALLEAgent(name = "Dalle", llm_config = {"config_list": self.dalle_llm_config})
        user_proxy = UserProxyAgent(
            name = "User_proxy", system_message = "A human admin.", human_input_mode = "NEVER", max_consecutive_auto_reply = 0, code_execution_config = False
        )
        
        # Ask the question with an image
        resp = user_proxy.initiate_chat(
            recipient = dalle,
            message = messages
        )
        
        return resp.summary, messages['content']
    
    def conclude_paragraph(self, content: str, gemini_key: str) -> str:
        url = f'https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={gemini_key}'
        headers = {'Content-Type': 'application/json'}

        content = json.loads(content)
        result = []
        for paragraph in content:
            flag = False
            for p in paragraph:
                if p["tag"] == "img":
                    flag = True
                    break
            
            if flag:
                prompt = f'''根據下方內容，彙整成一個最適合在google圖片搜尋的關鍵字後，並根據此關鍵字延伸出5個不同相關字，以json格式回覆，tag當中的文字固定為'關鍵字'以及'相關字'。
                            
                            ###內文不要用引號！！！###
                            
                            回傳格式：
                            [
                            關鍵字 => 主要關鍵字
                            相關字 => []
                            ]
                            {paragraph}
                            
                            Example:
                            [[{{
                                "tag": "關鍵字",
                                "content": "任天堂新遊戲"
                            }},
                            {{
                                "tag": "相關字",
                                "content": ["任天堂Switch", "Switch Lite", "Switch Pro", "標準版Switch", "Joy-Con控制器"]
                            }}],
                            ...]
                            '''

                data = {
                    "contents": [
                        {
                            "parts": [
                                {"text": prompt}
                            ]
                        }
                    ]
                }
                    
                response = requests.post(url, headers = headers, json = data)
                response = json.loads(response.text)["candidates"][0]["content"]["parts"][0]["text"]
                if "json" in response:
                    response = response[8: -3]
                response = response.replace("'", "\"")

                result.append(json.loads(response))
        
        return result
          
    def download_image(self, image_url: str) -> None:
        response = requests.get(image_url)
        if response.status_code == 200:
            folder_path = 'C:/python/AI_Website/resources/img'
            os.makedirs(folder_path, exist_ok = True)  # 確保目錄存在
            filename = "title.jpg"
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'wb') as f:
                f.write(response.content)
            print(f"圖片下載成功，已保存為 {filename}")
        else:
            print("圖片下載失敗")