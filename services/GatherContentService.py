import threading
import requests
import os
import sys

from bs4 import BeautifulSoup
from urllib.parse import urljoin
from alive_progress import alive_bar
from pathlib import Path
from typing import List
from readability import Document

from utils.YamlUtil import YamlUtil
from alive_progress import alive_bar
from utils.LogUtil import LogUtil

sys.path.append(str(Path(__file__).resolve().parent.parent))

class GatherContentService():
    def __init__(self, yaml: YamlUtil) -> None:
        self.log_util = LogUtil(__name__)
        self.user_agent = yaml.get_value("readability", "user_agent")
        self.base_url = "https://example.com"
        self.content = []
        self.img_tag = []
        self.new_img_tag = []

    def gather_website_content(self, urls: List[str], bar: alive_bar, thread_number: int) -> None:
        self.log_util.record_info(f"gather website content and img | thread number {thread_number}")
        for url in urls:
            try:
                response = requests.get(url, headers={"User-Agent": self.user_agent})
                document = Document(response.text)
                summary = document.summary()

                soup = BeautifulSoup(summary, "html.parser")
                img_tags = soup.find_all("img")
                img_urls = [img["src"] for img in img_tags if not img["src"].startswith("data:") or not img["src"].endswith(".svg")]
                
                self.content.append({"content": summary})

                for url in img_urls:
                    full_url = urljoin(self.base_url, url)
                    self.img_tag.append(full_url)
            except:
                pass
            finally:
                bar()

    def download_img(self, urls: List[str], bar: alive_bar, thread_number: int) -> None:
        self.log_util.record_info(f"download img | thread number: {thread_number}")

        # 獲取當前檔案的目錄
        code_dir = os.path.dirname(os.path.abspath(__file__))

        # 構建相對路徑
        resources_dir = os.path.join(code_dir, "..", "resources")
        img_dir = os.path.join(code_dir, "..", "resources", "img")
        
        os.makedirs(resources_dir, exist_ok=True)
        os.makedirs(img_dir, exist_ok=True)
        img_number = 1

        for url in urls:
            try: 
                response = requests.get(url)
                with open(f"{img_dir}/{thread_number+1}_img{img_number}.jpg", "wb") as file:
                    file.write(response.content)
                img_number += 1
                bar()
            except:
                pass


    def is_valid_image_url(self, urls: List[str], bar: alive_bar, thread_number: int) -> List[str]:
        self.log_util.record_info(f"detect image url valid | thread number: {thread_number}")
        temp = []
        for url in urls:
            try:
                if url.endswith("svg") is not True:
                    response = requests.get(url, timeout = 5)
                    if response.status_code == 200:
                        temp.append(url)
            except:
                pass
            finally:
                bar()
        self.new_img_tag[thread_number] = temp
        
        return temp
                
    def thread_gather_website_content(self, urls: List[str]) -> List[str]:
        thread_number = int(len(urls) / 50)
        chunk_size = int((len(urls) + thread_number - 1) // thread_number)
        url_chunks = [urls[i:i + chunk_size] for i in range(0, len(urls), chunk_size)]
        threads = []
        with alive_bar(len(urls)) as bar:
            for i in range(thread_number):
                thread = threading.Thread(target = self.gather_website_content, args = (url_chunks[i], bar, i))
                threads.append(thread)
                thread.start()
            for thread in threads:
                thread.join()
        return self.content
    
    def thread_download_img(self, urls: List[str]) -> List[str]:
        thread_number = len(urls)
        threads = []
        with alive_bar(sum(len(url) for url in urls)) as bar:
            for i in range(thread_number):
                thread = threading.Thread(target = self.download_img, args = (urls[i], bar, i))
                threads.append(thread)
                thread.start()
            for thread in threads:
                thread.join()

    def thread_is_valid_image_url(self, urls: List[str]) -> List[str]:
        thread_number = len(urls)
        threads = []
        self.new_img_tag = [[] for _ in range(thread_number)]
        with alive_bar(sum(len(url) for url in urls)) as bar:
            for i in range(thread_number):
                thread = threading.Thread(target = self.is_valid_image_url, args = (urls[i], bar, i))
                threads.append(thread)
                thread.start()
            for thread in threads:
                thread.join()
        return self.new_img_tag