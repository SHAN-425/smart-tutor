import streamlit as st
import plotly.express as px
import pandas as pd
import json
from agent import diagnose, generate_similar_questions

st.set_page_config(page_title="智慧学伴", layout="wide")

# --- 升级 1：初始化记忆（历史记录） ---
if "history" not in st.session_state:
    st.session_state.history = []

st.title("🧠 智慧学伴 — 学情诊断智能体")

# 侧边栏：显示历史记录
with st.sidebar:
    st.header("📚 学习记忆库")
    if not st.session_state.history:
        st.info("暂无历史记录，快来诊断第一道题吧！")
    else:
        for i, record in enumerate(reversed(st.session_state.history)):
            st.success(f"错题记录 {i+1}：{record['error_type']}")
            st.caption(f"原因：{record['diagnosis_reason']}")

st.subheader("📝 题目输入与诊断")
col_input, col_result = st.columns([1, 1.5])

with col_input:
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
                
                # 存入记忆
                st.session_state.history.append(result)
                
                with col_result:
                    st.subheader("📋 诊断报告")
                    st.error(f"错误类型：**{result['error_type']}**")
                    st.info(result["diagnosis_reason"])
                    st.markdown(f"**AI 提示：** {result['socratic_hint']}")
                    st.caption(f"涉及知识点：{'、'.join(result['knowledge_points'])}")
                    
                    # --- 升级 3：多维度雷达图 ---
                    st.subheader("📊 知识点掌握度")
                    # 读取大模型返回的多维度评分
                    scores = result.get("radar_scores", {"概念理解": 0.5, "计算能力": 0.5, "逻辑推理": 0.5})
                    df = pd.DataFrame({
                        "维度": list(scores.keys()),
                        "掌握度": list(scores.values())
                    })
                    fig = px.line_polar(df, r="掌握度", theta="维度", line_close=True)
                    fig.update_traces(fill="toself", line_color="rgb(255, 99, 71)") # 换个好看的颜色
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # --- 升级 2：变式题工具 ---
                    st.markdown("---")
                    if st.button("🔥 举一反三：生成变式题"):
                        with st.spinner("正在生成专属练习题..."):
                            similar_text = generate_similar_questions(result['knowledge_points'])
                            st.info(similar_text)
                            
            except json.JSONDecodeError:
                st.error("模型返回格式异常，请重试。")
            except Exception as e:
                st.error(f"调用失败：{e}")

            except json.JSONDecodeError:
                st.error("模型返回格式异常，请重试。")
            except Exception as e:
                st.error(f"调用失败：{e}")
