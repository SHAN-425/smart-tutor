import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv(ZHIPU_API_KEY), 
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

def diagnose(question, student_answer, correct_answer):
    prompt = f"""你是一个初中数学学情诊断专家。
题目：{question}
学生解答：{student_answer}
正确答案：{correct_answer}

请严格按以下JSON格式输出，不要输出其他内容：
{{
  "knowledge_points": ["知识点1"],
  "error_type": "概念不清/计算失误/逻辑断层/审题错误",
  "diagnosis_reason": "一句话解释",
  "socratic_hint": "一个启发式提问，不要直接给答案"
}}"""
    resp = client.chat.completions.create(
        model="qwen-plus",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    text = resp.choices[0].message.content.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0]
    return json.loads(text)