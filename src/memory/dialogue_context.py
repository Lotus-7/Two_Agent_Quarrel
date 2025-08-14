class DialogueContext:
    def __init__(self, window_size=6):
        self.xiaohei_history = []  # 存储小黑喵的说话内容
        self.xiaobai_history = []  # 存储小白喵的说话内容
        self.full_dialogue = []    # 存储完整对话记录
        self.window_size = window_size  # 保留最近N轮对话的窗口大小
        
        # 语义记忆摘要
        self.current_topic = ""     # 当前争议话题
        self.commitments = []       # 承诺记录
        self.mood_state = "conflict"  # 当前情绪状态: conflict/negotiating/resolving/resolved
        self.key_events = []        # 关键事件记录

    # 添加小黑喵的说话内容
    def add_xiaohei_response(self, response):
        entry = {"speaker": "xiaoheimiao", "content": response}
        self.xiaohei_history.append(entry)
        self.full_dialogue.append(entry)
        self._update_semantic_memory(response, "xiaoheimiao")

    # 添加小白喵的说话内容
    def add_xiaobai_response(self, response):
        entry = {"speaker": "xiaobaimiao", "content": response}
        self.xiaobai_history.append(entry)
        self.full_dialogue.append(entry)
        self._update_semantic_memory(response, "xiaobaimiao")

    # 语义记忆更新
    def _update_semantic_memory(self, response, speaker):
        # 检测承诺关键词
        promise_keywords = ["我会", "下次", "设闹钟", "记住", "不会忘", "保证", "答应", "承诺"]
        if any(keyword in response for keyword in promise_keywords):
            self.commitments.append({
                "speaker": speaker, 
                "promise": response, 
                "round": len(self.full_dialogue)
            })
        
        # 检测道歉/缓和关键词，但要更谨慎地转换情绪状态
        strong_softening = ["对不起", "抱歉", "原谅我", "我错了"]
        weak_softening = ["理解", "好嘛", "要得", "算了", "不生气"]
        
        strong_hit = any(keyword in response for keyword in strong_softening)
        weak_hit = any(keyword in response for keyword in weak_softening)
        
        # 更谨慎的情绪状态转换
        if strong_hit and self.mood_state == "conflict":
            self.mood_state = "negotiating"
        elif strong_hit and self.mood_state == "negotiating":
            self.mood_state = "resolving"
        elif weak_hit and self.mood_state == "resolving" and len(self.commitments) >= 2:
            self.mood_state = "resolved"
        
        # 检测升级冲突关键词
        conflict_keywords = ["又忘了", "怎么又", "还是", "每次都", "又来了", "老是", "又是", "就晓得"]
        if any(keyword in response for keyword in conflict_keywords):
            if self.mood_state in ["negotiating", "resolving"]:
                # 记录状态回退事件并重置情绪状态
                self.key_events.append(f"第{len(self.full_dialogue)}轮：{speaker}重提旧事，情绪回升")
                self.mood_state = "conflict"  # 重新回到冲突状态

    # 生成语义摘要提示
    def get_semantic_summary(self):
        if not self.full_dialogue:
            return ""
        
        summary_parts = []
        
        # 话题摘要
        if len(self.full_dialogue) >= 2:
            first_msg = self.full_dialogue[0]["content"]
            if "奶茶" in first_msg:
                self.current_topic = "忘记买奶茶"
            elif "约会" in first_msg or "计划" in first_msg:
                self.current_topic = "约会安排问题"
            elif "工作" in first_msg or "加班" in first_msg:
                self.current_topic = "工作忽视问题"
            else:
                self.current_topic = "生活琐事分歧"
            
            summary_parts.append(f"争议话题：{self.current_topic}")
        
        # 承诺摘要
        if self.commitments:
            recent_commitments = self.commitments[-2:]  # 最近2个承诺
            commitment_text = "；".join([c["promise"] for c in recent_commitments])
            summary_parts.append(f"已做承诺：{commitment_text}")
        
        # 情绪状态
        mood_map = {
            "conflict": "冲突中",
            "negotiating": "协商中", 
            "resolving": "缓和中",
            "resolved": "已和解"
        }
        summary_parts.append(f"当前状态：{mood_map.get(self.mood_state, '未知')}")
        
        # 关键事件提醒
        if self.key_events:
            latest_event = self.key_events[-1]
            summary_parts.append(f"注意：{latest_event}")
        
        return " | ".join(summary_parts)

    # 获取窗口化的对话历史（最近N轮 + 语义摘要）
    def get_contextual_dialogue(self):
        # 获取最近的对话
        recent_dialogue = self.full_dialogue[-self.window_size:] if len(self.full_dialogue) > self.window_size else self.full_dialogue
        
        return {
            "recent_dialogue": recent_dialogue,
            "semantic_summary": self.get_semantic_summary(),
            "full_length": len(self.full_dialogue)
        }

    # 获取小白喵说话内容
    def get_xiaobai_context(self):
        return self.xiaobai_history

    # 获取小黑喵说话内容
    def get_xiaohei_context(self):
        return self.xiaohei_history

    # 获取完整对话记录
    def get_full_dialogue(self):
        return self.full_dialogue
    
    # 检查是否应该自然结束
    def should_naturally_end(self):
        # 提高结束门槛：需要更多承诺和明确的和解状态
        if len(self.commitments) >= 3 and self.mood_state == "resolved":
            return True
        
        # 增加轮数门槛，避免过早结束（约18轮对话后才允许根据情绪结束）
        if len(self.full_dialogue) >= 36 and self.mood_state in ["resolving", "resolved"]:
            return True
            
        return False