import json
import re
from openai import OpenAI

# ==========================================
# ⚠️ 请把下面双引号里的内容，换成你真实的智谱 Key
# ==========================================
api_key = "sk-8ea27bed757a4037b8d4c94653d36090.7wIvZLeLrppXzOmc"

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
  "socratic_hint": "一个启发式提问，不要直接给答案",
  "radar_scores": {{
      "概念理解": 0.4,
      "计算能力": 0.6,
      "逻辑推理": 0.5
  }}
}}
注意：radar_scores 里的数值请根据学生错误情况，在 0.1 到 0.9 之间打分。"""
    
    resp = client.chat.completions.create(
        model="glm-4-flash",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    text = resp.choices[0].message.content.strip()
    
    # 提取 JSON 内容，防止大模型带废话
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        text = match.group(0)
        
    return json.loads(text)

def generate_similar_questions(knowledge_points):
    # 强化 Prompt：严禁输出公式符号或代码块，纯文字描述
    prompt = f"""请针对以下初中数学知识点，生成 2 道变式训练题。
知识点：{', '.join(knowledge_points)}
要求：
1. 难度由浅入深。
2. 给出题目和简短解答。
3. 【极其重要】：请直接使用纯文本输出，不要使用任何Markdown符号（如 #、** 等），不要使用 LaTeX 公式符号（如 \\( 或 \\frac 等），所有数学算式直接使用普通键盘字符表示（如 x^2 + 2x = 0），避免页面乱码。"""
    
    resp = client.chat.completions.create(
        model="glm-4-flash",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    
    text = resp.choices[0].message.content.strip()
    
    # 再次强效清洗：去掉可能残留的代码块标记
    text = text.replace("```markdown", "").replace("```json", "").replace("```", "")
    text = text.replace("\\(", "").replace("\\)", "").replace("$", "")
    
    return text.strip()
