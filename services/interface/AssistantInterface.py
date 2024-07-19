import time
import sys

from pathlib import Path
from abc import ABC, abstractmethod
from typing import List
from openai import OpenAI

from utils.LogUtil import LogUtil
from utils.YamlUtil import YamlUtil

sys.path.append(str(Path(__file__).resolve().parent.parent))

class AssistantInterface(ABC):
    def __init__(self, yaml: YamlUtil, target_function: str) -> None:
        self.log_util = LogUtil(__name__)
        self.client = OpenAI(api_key=yaml.get_value("ai_key", "openai"))
        self.assistant_id, self.vector_space_id = yaml.get_assistant_function(target_function)

    def upload_file(self, file_paths: List[str]) -> None:
        self.log_util.record_info("upload file")
        file_streams = [open(path, "rb") for path in file_paths]
        self.client.beta.vector_stores.file_batches.upload_and_poll(
            vector_store_id=self.vector_space_id, files=file_streams
        )

    def delete_file(self) -> None:
        self.log_util.record_info("delete file in vector space")
        files = self.client.beta.vector_stores.files.list(self.vector_space_id)
        for file in files:
            self.client.beta.vector_stores.files.delete(file_id = file.id, vector_store_id = self.vector_space_id)

    def create_thread(self) -> None:
        self.log_util.record_info("create thread")
        self.thread = self.client.beta.threads.create(
            tool_resources={
                "file_search": {
                    "vector_store_ids": [self.vector_space_id]
                }
            }
        )

    def update_assistant_instuction(self, prompt: str) -> None:
        self.log_util.record_info("update assistant instruction")
        self.client.beta.assistants.update(assistant_id = self.assistant_id, instructions = prompt)

    # add message to thread
    def add_message_thread(self, user_input: str) -> None:
        self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=user_input
        )

    # run the assistant
    def run_assistant(self) -> None:
        self.log_util.record_info("run assistant")
        self.run = self.client.beta.threads.runs.create(
            thread_id=self.thread.id,
            assistant_id=self.assistant_id
        )

    def get_assistant_response(self) -> None:
        self.log_util.record_info("get assistant response")
        while True:
            time.sleep(15)
            run_status = self.client.beta.threads.runs.retrieve(
                thread_id=self.thread.id,
                run_id=self.run.id
            )
            if run_status.status == 'completed':
                messages = self.client.beta.threads.messages.list(
                    thread_id=self.thread.id
                )
                # Loop through messages and print content based on role
                for msg in messages.data:
                    content = msg.content[0].text.value
                    return content
            else:
                self.log_util.record_info(run_status.status)
    
    @abstractmethod
    def start_assistant(self, file_paths: List[str], prompt: str = None) -> str:
        pass