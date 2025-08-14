from agents.xiaoheimiao import XiaoheiMiaoAgent
from agents.xiaobaimiao import XiaobaiMiaoAgent
from memory.dialogue_context import DialogueContext


def main():
    xiaohei = XiaoheiMiaoAgent()  # 男朋友 Agent（DeepSeek）
    xiaobai = XiaobaiMiaoAgent()  # 女朋友 Agent（GLM-4-Flash-250414）
    context = DialogueContext()   # 对话上下文（带语义摘要和窗口）

    print("----小白喵 vs 小黑喵 吵架对话开始----\n")

    # 第一轮：小白喵因为随机事件表达不满
    xiaobai_msg = xiaobai.start_conversation(context.get_contextual_dialogue())
    print(f"小白喵: {xiaobai_msg}")
    context.add_xiaobai_response(xiaobai_msg)

    # 多轮对话，直到自然结束
    max_rounds = 20
    rounds = 0
    while rounds < max_rounds:
        # 小黑喵回复（使用窗口化历史 + 语义摘要）
        xiaohei_response = xiaohei.respond(context.get_contextual_dialogue())
        print(f"\n小黑喵: {xiaohei_response}")
        context.add_xiaohei_response(xiaohei_response)

        # 新的自然结束判断：关键词 or 语义结束
        if should_end_session(xiaohei_response, is_xiaohei=True) or context.should_naturally_end():
            break

        # 小白喵回复（使用窗口化历史 + 语义摘要）
        xiaobai_response = xiaobai.respond(context.get_contextual_dialogue())
        print(f"\n小白喵: {xiaobai_response}")
        context.add_xiaobai_response(xiaobai_response)

        if should_end_session(xiaobai_response, is_xiaohei=False) or context.should_naturally_end():
            break

        rounds += 1

    print("\n【对话结束】")

    # 打印完整对话记录
    print("\n完整对话记录：")
    for idx, entry in enumerate(context.get_full_dialogue(), 1):
        print(f"{idx}. {entry['speaker']}: {entry['content']}")


# 自然结束条件：包含理解、道歉、承诺或“再聊/改天/抱歉/对不起/谢谢/理解/我会/计划/安排”等关键词
# 并保留一个最大轮数兜底

def should_end_session(response, is_xiaohei):
    # 提高结束阈值：需要检测到多个强信号且靠近尾部才结束
    strong_signals = ["对不起", "抱歉", "原谅我", "我会改", "保证", "答应你", "承诺"]
    weak_signals = ["理解", "谢谢", "安排", "计划", "改天", "再聊", "放下", "冷静", "再见", "好嘛", "要得"]
    
    strong_hit = sum(s in response for s in strong_signals)
    weak_hit = sum(w in response for w in weak_signals)
    
    # 强信号>=1且弱信号>=2才算结束，避免过早收尾
    return strong_hit >= 1 and weak_hit >= 2


if __name__ == "__main__":
    main()