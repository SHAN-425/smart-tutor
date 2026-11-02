import streamlit as st
import plotly.express as px
import pandas as pd
from agent import diagnose, generate_similar_questions

st.set_page_config(page_title="智慧学伴", layout="wide")

# 初始化记忆状态
if "history" not in st.session_state:
    st.session_state.history = []
if "current_result" not in st.session_state:
    st.session_state.current_result = None
if "similar_questions" not in st.session_state:
    st.session_state.similar_questions = None

st.title("🧠 智慧学伴 — 学情诊断智能体")

# 侧边栏：学习记忆库
with st.sidebar:
    st.header("📚 学习记忆库")
    if not st.session_state.history:
        st.info("暂无历史记录，快来诊断第一道题吧！")
    else:
        for i, record in enumerate(reversed(st.session_state.history)):
            st.success(f"错题 {i+1}：{record.get('error_type', '未知')}")
            st.caption(f"原因：{record.get('diagnosis_reason', '无')}")

col_input, col_result = st.columns([1, 1.5])

# 左侧：输入区
with col_input:
    st.subheader("📝 题目输入")
    question = st.text_area("题目")
    student_answer = st.text_area("你的解答")
    correct_answer = st.text_area("正确答案")
    run = st.button("开始诊断", type="primary", use_container_width=True)

# 处理诊断请求
if run:
    if not all([question, student_answer, correct_answer]):
        st.warning("请填写全部字段")
    else:
        with st.spinner("AI 老师诊断中…"):
            try:
                result = diagnose(question, student_answer, correct_answer)
                st.session_state.current_result = result
                st.session_state.similar_questions = None # 重置之前的变式题
                st.session_state.history.append(result)
            except Exception as e:
                st.error(f"诊断失败：{e}")

# 右侧：结果展示区
if st.session_state.current_result:
    result = st.session_state.current_result
    with col_result:
        st.subheader("📋 诊断报告")
        st.error(f"错误类型：**{result.get('error_type', '未知')}**")
        st.info(result.get('diagnosis_reason', '无'))
        st.markdown(f"**AI 提示：** {result.get('socratic_hint', '无')}")
        st.caption(f"涉及知识点：{'、'.join(result.get('knowledge_points', []))}")
        
        st.subheader("📊 知识点掌握度")
        scores = result.get("radar_scores", {"概念理解": 0.5, "计算能力": 0.5, "逻辑推理": 0.5})
        df = pd.DataFrame({
            "维度": list(scores.keys()),
            "掌握度": list(scores.values())
        })
        fig = px.line_polar(df, r="掌握度", theta="维度", line_close=True)
        fig.update_traces(fill="toself", line_color="rgb(255, 99, 71)")
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # 变式题生成按钮
        if st.button("🔥 举一反三：生成变式题", use_container_width=True):
            with st.spinner("正在生成专属练习题..."):
                try:
                    kps = result.get('knowledge_points', ["基础数学"])
                    if not kps:
                        kps = ["基础数学"]
                    similar_text = generate_similar_questions(kps)
                    st.session_state.similar_questions = similar_text
                except Exception as e:
                    st.error(f"生成题目失败：{e}")

        # 变式题展示区 (使用 st.text 纯文本展示，绝对无乱码)
        if st.session_state.similar_questions:
            st.success("🎯 专属变式题已生成：")
            # 用 st.text 保证原样输出，不解析任何符号
            st.text(st.session_state.similar_questions)
