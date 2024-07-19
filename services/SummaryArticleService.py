import sys
import json

from pathlib import Path
from typing import List

from utils.YamlUtil import YamlUtil
from utils.FunctionsUtil import FunctionsUtil
from utils.LogUtil import LogUtil
from services.interface.AssistantInterface import AssistantInterface

sys.path.append(str(Path(__file__).resolve().parent.parent))

class SummaryArticleService(AssistantInterface):
    def __init__(self, yaml: YamlUtil):
        super().__init__(yaml, 'summary_article')
        self.log_util = LogUtil(__name__)
        self.function_util = FunctionsUtil()

    def start_assistant(self, file_paths: List[str], prompt: str = None) -> str:
        while True:
            self.log_util.record_info("summarize article")
            # upload file
            self.upload_file(file_paths)
            # create thread
            self.create_thread()
            # update assistant instruction
            self.update_assistant_instuction(prompt)
        
            # run assistant
            self.run_assistant()
            # get result
            result = self.get_assistant_response()
            while result[0] in ("`", "\n") or result[: 4] == "json":
                if result[0] in ("`", "\n"):
                    result = result[1: ]
                else:
                    result = result[5: ]
                while result[-1] in ("`", "\n"):
                    result = result[: -1]
                    
            # delete assistant vector space
            self.delete_file()
            if self.function_util.validate_input(result):
                return json.loads(result)