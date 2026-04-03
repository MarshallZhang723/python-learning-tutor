# Python 学习辅助助手

一个面向初学者的交互式 Python 学习工具，基于 Streamlit + LangChain (Claude) 构建。

## 功能

- **学习**：按章节学习 Python 核心概念（变量、数据类型、循环、函数、装饰器），每个概念都有可运行的代码示例
- **练习**：挑战编程题目，系统自动评分
- **提问**：粘贴代码，AI 用中文为你解释错误、优化建议或回答问题
- **进度**：查看学习进度和错题记录

## 安装

```bash
# 1. 克隆或下载项目
cd Project

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置 API Key
cp .env.example .env
# 编辑 .env 文件，填入你的 Anthropic API Key
```

## 运行

```bash
streamlit run app.py
```

浏览器会自动打开 http://localhost:8501。

## 项目结构

```
├── app.py                  # Streamlit 入口
├── config.py               # 全局配置
├── core/                   # 业务逻辑
│   ├── code_executor.py    # 沙箱代码执行（multiprocessing 进程隔离）
│   ├── grader.py           # 测试用例评分
│   ├── llm_client.py       # LangChain + Claude 集成
│   └── progress_tracker.py # JSON 进度持久化
├── courses/                # 课程内容（JSON）
│   ├── variables.json
│   ├── data_types.json
│   ├── loops.json
│   ├── functions.json
│   └── decorators.json
├── data/                   # 运行时用户数据
├── ui/                     # Streamlit UI 层
│   ├── components.py       # 可复用组件
│   └── pages.py            # 页面布局
└── tests/                  # 单元测试
```

## 课程内容

| 课程 | 章节 | 练习 |
|------|------|------|
| 变量与赋值 | 3 课 | 3 题 |
| 数据类型 | 4 课 | 3 题 |
| 循环 | 3 课 | 3 题 |
| 函数 | 3 课 | 3 题 |
| 装饰器 | 4 课 | 2 题 |

## 技术栈

- Python 3.9+
- Streamlit（Web UI）
- LangChain + Anthropic Claude（AI 集成）
- JSON 文件（本地数据存储）
