import os
from .base_agent import BaseAgent

class XiaoheiMiaoAgent(BaseAgent):
    def __init__(self, deepseek_api_key=None):
        if deepseek_api_key is None:
            deepseek_api_key = os.environ.get("DEEPSEEK_API_KEY", "YOUR_API_KEY")
        deepseek_model_config = {
            "api_key": deepseek_api_key,
            "base_url": "https://api.deepseek.com",
            "model": "deepseek-chat"
        }
        super().__init__("prompts/xiaoheimiao_prompt.yaml", model_config=deepseek_model_config)

    def respond(self, dialogue_context):
        """
        dialogue_context: 期望为 DialogueContext.get_contextual_dialogue() 的返回值，结构：
        {
            "recent_dialogue": [...],
            "semantic_summary": str,
            "full_length": int
        }
        """
        messages = [
            {"role": "system", "content": self.config["system_prompt"]}
        ]

        # 注入语义摘要，帮助模型承接上下文与承诺
        semantic_summary = dialogue_context.get("semantic_summary") if isinstance(dialogue_context, dict) else None
        if semantic_summary:
            messages.append({
                "role": "system",
                "content": f"对话摘要（需保持一致并承接）：{semantic_summary}。请避免重复开启新话题，优先回应对方前一轮内容，并对既有承诺给出具体落实。"
            })

        recent_dialogue = dialogue_context.get("recent_dialogue", []) if isinstance(dialogue_context, dict) else dialogue_context

        # 添加对话历史：对方(小白喵)作为user，自己(小黑喵)作为assistant
        for entry in recent_dialogue:
            if entry["speaker"] == "xiaobaimiao":
                messages.append({
                    "role": "user",  # 小白喵作为用户输入
                    "content": entry["content"]
                })
            else:
                messages.append({
                    "role": "assistant",  # 小黑喵自己的历史发言
                    "content": entry["content"]
                })

        return self.generate_response(messages)