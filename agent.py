import os
import json
from openai import OpenAI

# 从环境变量读取（本地测试如果在 .env 里配了就生效，云端读 Secrets）
api_key = os.environ.get("ZHIPU_API_KEY")
client = OpenAI(
    api_key=api_key,
    base_url="https://open.bigmodel.cn/api/paas/v4"
)

def diagnose(question, student_answer, correct_answer):
    # 注意：升级了Prompt，让大模型多输出一个 radar_scores 用于雷达图
    prompt = f"""你是一个初中数学学情诊断专家。
题目：{question}
学生解答：{student_answer}
正确答案：{correct_answer}

请严格按以下JSON格式输出，不要输出其他内容：
{{
  "knowledge_points": ["知识点1"],
  "error_type": "概念不清/计算失误/逻辑断层/审题错误",
  "diagnosis_reason": "一句话解释",
  "socratic_hint": "一个启发式提问，不要直接给答案",
  "radar_scores": {{
      "概念理解": 0.4,
      "计算能力": 0.6,
      "逻辑推理": 0.5
  }}
}}
注意：radar_scores 里的数值请根据学生错误情况，在 0.1 到 0.9 之间随机打分。"""
    
    resp = client.chat.completions.create(
        model="glm-4-flash",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    text = resp.choices[0].message.content.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0]
    return json.loads(text)

# 新增：生成变式题的工具函数
def generate_similar_questions(knowledge_points):
    prompt = f"""请针对以下知识点，生成 2 道初中数学变式训练题，难度逐渐递增。
知识点：{', '.join(knowledge_points)}
请直接输出题目和简短答案，格式清晰。"""
    
    resp = client.chat.completions.create(
        model="glm-4-flash",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return resp.choices[0].message.content.strip()
