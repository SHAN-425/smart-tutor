import os
import json
from openai import OpenAI

# 注意：这里使用的是 os.environ 来读取云端配置的 Secrets
api_key = os.environ.get("ZHIPU_API_KEY")
client = OpenAI(
    api_key=api_key,
    base_url="https://open.bigmodel.cn/api/paas/v4"
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
        model="glm-4-flash", # 如果你用智谱，这里一般是 glm-4-flash
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    text = resp.choices[0].message.content.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0]
    return json.loads(text)
