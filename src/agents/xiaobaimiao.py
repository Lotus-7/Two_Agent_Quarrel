import os
from .base_agent import BaseAgent

class XiaobaiMiaoAgent(BaseAgent):
    def __init__(self, glm_api_key=None):
        if glm_api_key is None:
            glm_api_key = os.environ.get("ZHIPU_API_KEY", "YOUR_API_KEY")
        glm_model_config = {
            "api_key": glm_api_key,
            "base_url": "https://open.bigmodel.cn/api/paas/v4",
            "model": "glm-4-flash-250414"
        }
        super().__init__("prompts/xiaobaimiao_prompt.yaml", model_config=glm_model_config)

    def start_conversation(self, dialogue_context=None):
        # 第一轮：随机事件引发不满
        messages = [
            {"role": "system", "content": self.config["system_prompt"]}
        ]

        # 如果有摘要（例如第二次启动或外部传入），也一并注入
        if dialogue_context and isinstance(dialogue_context, dict):
            semantic_summary = dialogue_context.get("semantic_summary")
            if semantic_summary:
                messages.append({
                    "role": "system",
                    "content": f"对话摘要（用于保持一致）：{semantic_summary}。第一句话请自然引出冲突点，避免重复。"
                })

        messages.append({"role": "user", "content": self.config["user_prompt"]})
        return self.generate_response(messages)

    def respond(self, dialogue_context):
        """
        dialogue_context: 期望为 DialogueContext.get_contextual_dialogue() 的返回值
        {"recent_dialogue": [...], "semantic_summary": str, "full_length": int}
        """
        messages = [
            {"role": "system", "content": self.config["system_prompt"]}
        ]

        # 注入语义摘要
        semantic_summary = dialogue_context.get("semantic_summary") if isinstance(dialogue_context, dict) else None
        if semantic_summary:
            messages.append({
                "role": "system",
                "content": f"对话摘要（需保持一致并承接）：{semantic_summary}。请避免重复开启新话题，优先回应对方前一轮内容，并在情绪缓和后逐步收尾。"
            })

        recent_dialogue = dialogue_context.get("recent_dialogue", []) if isinstance(dialogue_context, dict) else dialogue_context

        # 添加对话历史（自身assistant，对方user）
        for entry in recent_dialogue:
            if entry["speaker"] == "xiaoheimiao":
                messages.append({
                    "role": "user",  # 小黑喵作为对方输入
                    "content": entry["content"]
                })
            else:
                messages.append({
                    "role": "assistant",  # 小白喵自己的历史发言
                    "content": entry["content"]
                })
        return self.generate_response(messages)