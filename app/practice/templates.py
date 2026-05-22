"""Question type templates and helpers."""

from enum import Enum


class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    FILL_BLANK = "fill_blank"


QUESTION_TEMPLATES = {
    QuestionType.MULTIPLE_CHOICE: (
        "基于以下知识点，生成一道选择题（4个选项）。"
        "用以下JSON格式输出（不要输出其他内容）：\n"
        '{{"question": "题目内容", "options": ["A. 选项1", "B. 选项2", "C. 选项3", "D. 选项4"], '
        '"answer": "A", "explanation": "解析"}}'
    ),
    QuestionType.TRUE_FALSE: (
        "基于以下知识点，生成一道判断题。"
        "用以下JSON格式输出（不要输出其他内容）：\n"
        '{{"question": "题目内容", "answer": "对", "explanation": "解析"}}'
    ),
    QuestionType.SHORT_ANSWER: (
        "基于以下知识点，生成一道简答题。"
        "用以下JSON格式输出（不要输出其他内容）：\n"
        '{{"question": "题目内容", "answer": "参考答案", "explanation": "答题要点"}}'
    ),
    QuestionType.FILL_BLANK: (
        "基于以下知识点，生成一道填空题（用____标记空白处）。"
        "用以下JSON格式输出（不要输出其他内容）：\n"
        '{{"question": "题目内容（含____）", "answer": "正确答案", "explanation": "解析"}}'
    ),
}


# Default weights for random question type selection
DEFAULT_TYPE_WEIGHTS = {
    QuestionType.MULTIPLE_CHOICE: 0.40,
    QuestionType.TRUE_FALSE: 0.20,
    QuestionType.SHORT_ANSWER: 0.25,
    QuestionType.FILL_BLANK: 0.15,
}
