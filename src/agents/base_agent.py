import os
import yaml
from openai import OpenAI

class BaseAgent:
    def __init__(self, config_path, model_config=None):
        self.config = self._load_config(config_path)
        
        # 默认使用DeepSeek配置
        if model_config is None:
            model_config = {
                "api_key": "YOUR_API_KEY",  # 请填写你的 API Key
                "base_url": "https://api.deepseek.com",
                "model": "deepseek-chat"
            }
        
        self.model_config = model_config
        self.client = OpenAI(
            api_key=model_config["api_key"],
            base_url=model_config["base_url"]
        )

    def _load_config(self, config_path):
        # 如果是相对路径，则基于项目根目录（本文件上上级目录的上一级）进行解析
        if not os.path.isabs(config_path):
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            candidate = os.path.join(project_root, config_path)
            if os.path.exists(candidate):
                config_path = candidate
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    def generate_response(self, messages):
        response = self.client.chat.completions.create(
            model=self.model_config["model"],
            messages=messages
        )
        return response.choices[0].message.content