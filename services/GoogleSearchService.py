import urllib.request as request
import urllib.parse
import json
import time
import sys
import ssl

from alive_progress import alive_bar
from pathlib import Path
from ast import keyword
from typing import List

from utils.LogUtil import LogUtil

sys.path.append(str(Path(__file__).resolve().parent.parent))

class GoogleSearchService():
    def __init__(self) -> None:
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        self.log_util = LogUtil(__name__)

    def google_search(self, keywords: str) -> List[str]:
        self.log_util.record_info("get url from google search api")
        context = ssl._create_unverified_context()
        links = []
        with alive_bar(len(keywords) * 10) as bar:
            for keyword in keywords:
                try: 
                    params = {
                        'cx': '15fd44675653940b9',
                        'key': '',
                        'excludeTerms': 'youtube meta facebook download amazon shopee douyin tiktok taobao weibo',
                        'lr': 'lang_en',
                        'gl': 'us',
                        'cr': 'countryUS',
                        'hl': 'en',
                        'c2coff': '1',
                        'sort': 'date',
                        #'searchType': 'image',
                        'fields': 'items(link)',
                        'q': keyword
                    }
                    url = f"{self.base_url}?{urllib.parse.urlencode(params)}"
                    with request.urlopen(url, context=context) as response:
                        data = json.load(response)

                    for i in range(10):
                        l = data["items"][i]["link"]
                        links.append(l)
                    time.sleep(0.1)
                except:
                    pass
                finally:
                    bar(10)
                    
        return links
    
    def google_search_image(self, contents):
        self.log_util.record_info("get image url from google search api")
        context = ssl._create_unverified_context()
        links = []
        with alive_bar(len(contents) * 150) as bar:
            for content in contents:
                try:
                    w1, w2 = content[0]["content"], content[1]["content"]
                    if w2:
                        words = w2
                    else:
                        words = [w1]
                        
                    temp = []
                    for word in words:
                        for num in range(0, 21, 10):
                            try: 
                                params = {
                                    'cx': '15fd44675653940b9',
                                    'key': '',
                                    'lr': 'lang_en',
                                    'gl': 'us',
                                    'cr': 'countryUS',
                                    'hl': 'en',
                                    'c2coff': '1',
                                    'sort': 'date',
                                    'searchType': 'image',
                                    'fields': 'items(link)',
                                    'start': num,
                                    'q': word
                                }
                                url = f"{self.base_url}?{urllib.parse.urlencode(params)}"
                                with request.urlopen(url, context=context) as response:
                                    data = json.load(response)

                                for i in range(10):
                                    l = data["items"][i]["link"]
                                    temp.append(l)
                                time.sleep(0.1)
                            except:
                                pass
                            finally:
                                bar(10)
                    links.append(temp)
                except:
                    pass
                
        return links