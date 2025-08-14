# 两个 Agent 吵架

这是一个模拟情侣对话的双 Agent 系统，其中"小白喵"（女朋友）和"小黑喵"（男朋友）能够进行带有情感色彩和记忆连续性的对话。系统具备语义记忆、情绪状态跟踪和自然结束判断等功能。

> 注意：prompt 未完善，仅测试可以对话。

## 项目结构

```
Two_Agent_Quarrel/
├── requirements.txt              # Python依赖包
├── prompts/                      # 提示词配置目录
│   ├── xiaobaimiao_prompt.yaml   # 小白喵角色提示词
│   └── xiaoheimiao_prompt.yaml   # 小黑喵角色提示词
└── src/                          # 源代码目录
    ├── __init__.py
    ├── main.py                   # 主程序入口
    ├── agents/                   # Agent实现目录
    │   ├── __init__.py
    │   ├── base_agent.py         # Agent基类
    │   ├── xiaobaimiao.py        # 小白喵Agent
    │   └── xiaoheimiao.py        # 小黑喵Agent
    └── memory/                   # 记忆系统目录
        ├── __init__.py
        └── dialogue_context.py   # 对话上下文管理
```

## 使用说明

确保安装 Python 和 openai 库。

```bash
pip install openai
```

### 配置

在 `src/agents/xiaobaimiao.py` 和 `src/agents/xiaoheimiao.py` 中配置你的 API KEY 密钥。**此代码中使用的是 DeepSeek 和 GLM 模型**

### 运行

```bash
python src/main.py
```
