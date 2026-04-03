import config

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate


ERROR_ANALYSIS_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "你是一位耐心的 Python 编程老师。请用中文解释代码错误的原因，并给出修复建议。"
            "回答要清晰易懂，适合初学者理解。",
        ),
        (
            "human",
            "以下是我的 Python 代码：\n```python\n{user_code}\n```\n\n"
            "运行时出现了以下错误：\n```\n{error_message}\n```\n\n"
            "请帮我分析错误原因，并告诉我如何修复。",
        ),
    ]
)

STYLE_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "你是一位经验丰富的 Python 开发者。请用中文分析代码的风格问题，"
            "并提供符合 Pythonic 风格的改进建议。回答要简洁实用。",
        ),
        (
            "human",
            "以下是我的 Python 代码：\n```python\n{user_code}\n```\n\n"
            "请帮我检查代码风格，给出 Pythonic 的改进建议。",
        ),
    ]
)

QA_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "你是一位耐心的 Python 编程老师。请用中文回答学生的问题。"
            "如果提供了代码上下文，请结合代码来解释。回答要清晰易懂。",
        ),
        (
            "human",
            "以下是我的 Python 代码：\n```python\n{user_code}\n```\n\n"
            "我的问题是：{user_question}",
        ),
    ]
)


class LLMClient:
    def __init__(self):
        if not config.ANTHROPIC_API_KEY:
            raise ValueError(
                "请在 .env 文件中设置 ANTHROPIC_API_KEY"
            )
        self.llm = ChatAnthropic(
            model=config.ANTHROPIC_MODEL,
            api_key=config.ANTHROPIC_API_KEY,
            max_tokens=2048,
        )

    def analyze_error(self, code, error):
        """Analyze a code error and return a Chinese explanation."""
        chain = ERROR_ANALYSIS_PROMPT | self.llm
        response = chain.invoke({"user_code": code, "error_message": error})
        return response.content

    def analyze_error_stream(self, code, error):
        """Stream the error analysis response."""
        chain = ERROR_ANALYSIS_PROMPT | self.llm
        for chunk in chain.stream({"user_code": code, "error_message": error}):
            yield chunk.content

    def suggest_style(self, code):
        """Suggest Pythonic style improvements."""
        chain = STYLE_PROMPT | self.llm
        response = chain.invoke({"user_code": code})
        return response.content

    def suggest_style_stream(self, code):
        """Stream style suggestions."""
        chain = STYLE_PROMPT | self.llm
        for chunk in chain.stream({"user_code": code}):
            yield chunk.content

    def answer_question(self, code, question):
        """Answer a question about Python code."""
        chain = QA_PROMPT | self.llm
        response = chain.invoke({"user_code": code, "user_question": question})
        return response.content

    def answer_question_stream(self, code, question):
        """Stream the Q&A response."""
        chain = QA_PROMPT | self.llm
        for chunk in chain.stream({"user_code": code, "user_question": question}):
            yield chunk.content
