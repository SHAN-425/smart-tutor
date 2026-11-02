import streamlit as st
import plotly.express as px
import pandas as pd
import json
from agent import diagnose

st.set_page_config(page_title="智慧学伴", layout="wide")
st.title("🧠 智慧学伴 — 学情诊断智能体")

with st.sidebar:
    st.header("输入")
    question = st.text_area("题目")
    student_answer = st.text_area("你的解答")
    correct_answer = st.text_area("正确答案")
    run = st.button("开始诊断", type="primary")

if run:
    if not all([question, student_answer, correct_answer]):
        st.warning("请填写全部字段")
    else:
        with st.spinner("AI 老师诊断中…"):
            try:
                result = diagnose(question, student_answer, correct_answer)

                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("📋 诊断报告")
                    st.error(f"错误类型：**{result['error_type']}**")
                    st.info(result["diagnosis_reason"])
                    st.markdown(f"**AI 提示：** {result['socratic_hint']}")
                    st.caption(f"涉及知识点：{'、'.join(result['knowledge_points'])}")

                with col2:
                    st.subheader("📊 知识点掌握度")
                    kps = result["knowledge_points"] or ["未识别"]
                    df = pd.DataFrame({
                        "知识点": kps,
                        "掌握度": [0.4] * len(kps)
                    })
                    fig = px.line_polar(df, r="掌握度", theta="知识点", line_close=True)
                    fig.update_traces(fill="toself")
                    st.plotly_chart(fig, use_container_width=True)

            except json.JSONDecodeError:
                st.error("模型返回格式异常，请重试。")
            except Exception as e:
                st.error(f"调用失败：{e}")