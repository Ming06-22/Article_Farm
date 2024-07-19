import json
import os
import pdb
import random
import re
import time
import PIL
import requests
import autogen
import matplotlib.pyplot as plt

from diskcache import Cache
from openai import OpenAI
from PIL import Image
from termcolor import colored
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union

from autogen import Agent, AssistantAgent, ConversableAgent, UserProxyAgent
from autogen.agentchat.contrib.img_utils import _to_pil, get_image_data, get_pil_image, gpt4v_formatter
from autogen.agentchat.contrib.multimodal_conversable_agent import MultimodalConversableAgent

class DALLEAgent(ConversableAgent):
    def __init__(self, name, llm_config: dict, **kwargs):
        super().__init__(name, llm_config = llm_config, **kwargs)

        config_list = llm_config["config_list"]
        api_key = config_list[0]["api_key"] # 從config_list列表中的第一個元素提取 api_key
        
        self._dalle_client = OpenAI(api_key = api_key)
        self.register_reply([Agent, None], DALLEAgent.generate_dalle_reply)

    def dalle_call(self, model: str, prompt: str, size: str, quality: str, n: int) -> str:
        # 如果不在緩存目錄中，則計算並儲存結果 
        response = self._dalle_client.images.generate( 
            model = model,
            prompt = prompt,
            size = size,
            quality = quality,
            n = n,
        )
        image_url = response.data[0].url
        
        return image_url

    def extract_img(self, agent: Agent):
        last_message = agent.last_message()["content"]

        if isinstance(last_message, str):
            img_data = re.findall("<img (.*)>", last_message)[0]
        elif isinstance(last_message, list):
            # The GPT-4V format, where the content is an array of data
            assert isinstance(last_message[0], dict)
            img_data = last_message[0]["image_url"]["url"]

        pil_img = get_pil_image(img_data)
        
        return pil_img

    def send(self, message: Union[Dict, str], recipient: Agent, request_reply: Optional[bool] = None, silent: Optional[bool] = False):
        # override and always "silent" the send out message;
        # otherwise, the print log would be super long!
        super().send(message, recipient, request_reply, silent=False)
        
    def generate_dalle_reply(self, messages: Optional[List[Dict]], sender: "Agent", config):
        # 使用 OpenAI DALLE 調用生成回覆
        client = self._dalle_client if config is None else config
        if client is None:
            return False,None
        if messages is None:
            messages = self._oai_message[sender]

        prompt = messages[-1]["content"]
        size = messages[-1]["size"]
        quality = messages[-1]["quality"]

        img_url = self.dalle_call(
            model = "dall-e-3",
            prompt = prompt,
            size = size,
            quality = quality,
            n = 1
        )
              
        # 返回OpenAI訊息格式
        return True, img_url