import streamlit as st
import sys
import os
import time
import asyncio
import pandas as pd

# 1. 架构适配：将根目录加入路径，确保能导入 src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.core.llm_engine import AnalysisEngine
from src.core.asr_client import ASRClient
from src.database.repository import ConsultationRepository
from config.settings import settings

# ================= CSS 美化 =================
st.set_page_config(page_title=f"{settings.APP_NAME}", page_icon="🦷", layout="wide")
st.markdown("""
<style>
    .stApp { background-color: #F8F9FA; }
    h1, h2, h3 { color: #008080 !important; }
    
    /* 聊天气泡：咨询师 (左蓝) */
    .chat-doctor { 
        background-color: #E3F2FD; border-radius: 15px 15px 15px 0; 
        padding: 10px; margin: 5px; float: left; clear: both; 
        color: #1565C0; max-width: 80%; box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    /* 聊天气泡：患者 (右白) */
    .chat-patient { 
        background-color: #FFF; border: 1px solid #DDD; 
        border-radius: 15px 15px 0 15px; padding: 10px; margin: 5px; 
        float: right; clear: both; color: #333; max-width: 80%; box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    .speaker-label { font-size: 0.8rem; color: #999; clear: both; display: block; margin-top: 5px; }
    
    /* 表格容器背景 */
    div[data-testid="stDataFrame"] { background-color: white; padding: 10px; border-radius: 8px; border: 1px solid #eee; }
</style>
""", unsafe_allow_html=True)

# ================= 服务初始化 =================
if 'services' not in st.session_state:
    st.session_state.services = {
        'db': ConsultationRepository(),
        'analyst': AnalysisEngine(),
        'asr': ASRClient()
    }
services = st.session_state.services

# ================= 辅助函数 =================
def render_dialogue(text):
    """渲染气泡对话"""
    if not text or pd.isna(text) or str(text) == "nan":
        st.info("暂无对话记录")
        return
    text = str(text)
    
    # 模拟数据通常自带换行，ASR数据可能需要处理
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if not line: continue
        
        # 简单规则：默认说话人0是咨询师
        is_doctor = "说话人 0" in line or "咨询师" in line
        content = line.split("】")[-1].replace(":", "").strip() if "】" in line else line
        
        if is_doctor:
            st.markdown(f"<div><span class='speaker-label'>咨询师</span><div class='chat-doctor'>{content}</div></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='text-align:right'><span class='speaker-label'>患者</span><div class='chat-patient'>{content}</div></div>", unsafe_allow_html=True)
    
    st.markdown("<div style='clear:both'></div>", unsafe_allow_html=True)

# ================= 主程序 =================
def main():
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/dentist.png", width=80)
        st.title("智齿 · 咨询管家")
        role = st.selectbox("工作台", ["👨‍⚕️ 咨询师端", "📊 主管监管端"])
        
        st.divider()
        # 【新增】调试开关：一键切换真假数据
        use_mock = st.toggle("🛠️ 开启模拟数据 (免消耗)", value=True)

    # --- 咨询师端 ---
    if role == "👨‍⚕️ 咨询师端":
        st.header("👋 开始新的咨询质检")
        with st.container(border=True):
            c1, c2 = st.columns([1, 2])
            with c1:
                c_name = st.text_input("咨询师", "Dr. Zhang")
                p_name = st.text_input("患者姓名", "李先生")
                is_deal = st.selectbox("是否成交", ["否", "是"])
            with c2:
                uploaded_file = st.file_uploader("上传录音", type=['m4a', 'mp3', 'wav'])

        if st.button("🚀 立即分析", type="primary", use_container_width=True):
            if not uploaded_file and not use_mock:
                st.error("请先上传录音文件！")
                st.stop()
                
            status = st.status("正在处理...", expanded=True)
            try:
                transcript = ""
                
                # 1. 获取转写文本 (真/假 分流)
                if use_mock:
                    status.write("🛠️ [模拟模式] 加载测试文本...")
                    time.sleep(1) # 假装在跑
                    transcript = """
【说话人 0】: 您好，请问牙齿哪里不舒服？
【说话人 1】: 大牙疼，想拔了。
【说话人 0】: 别急，先拍片看看。您有高血压吗？
【说话人 1】: 没有。
【说话人 0】: 那我们先去检查一下。
                    """
                else:
                    status.write("☁️ [真实模式] 上传 OSS 并转写...")
                    file_bytes = uploaded_file.getvalue()
                    url = services['asr'].upload_to_oss(file_bytes, uploaded_file.name)
                    transcript = services['asr'].transcribe(url)

                # 【防御性编程】检查文本是否为空
                if not transcript or len(transcript) < 5:
                    status.update(label="❌ 转写失败", state="error")
                    st.error("转写结果为空！请检查：1.录音是否清晰 2.API Key是否欠费 3.网络连接")
                    st.stop()

                # 2. 智能分析
                status.write("🧠 AI 正在分析销售逻辑...")
                report = services['analyst'].analyze_consultation(transcript)
                
                # 3. 存库 (带对话实录)
                status.write("💾 保存至数据库...")
                services['db'].save_record(c_name, p_name, is_deal, report, transcript)
                
                status.update(label="✅ 完成！", state="complete", expanded=False)
                
                # 结果展示
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("得分", report.sales_score)
                c2.metric("意向", report.customer_intent)
                c3.info(f"建议: {report.next_step}")
                
                t1, t2 = st.tabs(["💡 诊断报告", "📝 对话实录"])
                with t1:
                    st.success(f"优点：{report.good_points}")
                    st.error(f"失误：{report.bad_points}")
                with t2:
                    render_dialogue(transcript)

            except Exception as e:
                status.update(label="❌ 系统错误", state="error")
                st.error(f"Error: {str(e)}")

    # --- 主管端 (全能重构版) ---
    elif role == "📊 主管监管端":
        st.markdown("## 📊 全局监管看板")
        
        # 顶部工具栏
        col_tool1, col_tool2 = st.columns([6, 1])
        with col_tool1:
            st.caption(f"数据最后更新: {time.strftime('%H:%M:%S')}")
        with col_tool2:
            if st.button("🔄 刷新", use_container_width=True):
                st.rerun()
            
        df = services['db'].load_records()
        
        if not df.empty:
            # 数据预处理
            df["评分"] = pd.to_numeric(df["评分"], errors='coerce').fillna(0).astype(int)
            df["成交状态"] = df["是否成交"].apply(lambda x: "✅ 成交" if x == "是" else "⏳ 待定")
            
            # --- 1. 核心指标卡 (KPI Cards) ---
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("总接待量", f"{len(df)}", delta="今日")
            
            deal_rate = (len(df[df['是否成交']=='是']) / len(df) * 100)
            k2.metric("成交率", f"{deal_rate:.1f}%", delta_color="normal" if deal_rate > 30 else "inverse")
            
            avg_score = df['评分'].mean()
            k3.metric("平均话术分", f"{avg_score:.1f}", delta=f"{avg_score-80:.1f} vs基准")
            
            low_score_count = len(df[df['评分'] < 60])
            k4.metric("高危预警", f"{low_score_count} 单", delta="需复盘", delta_color="inverse")
            
            st.divider()
            
            # --- 2. 交互式数据表格 (Data Grid) ---
            st.subheader("📋 咨询记录检索")
            
            # 使用 data_editor 代替简单的 dataframe，支持排序和筛选
            # 仅展示关键字段
            grid_df = df[["时间", "咨询师", "患者姓名", "评分", "成交状态", "客户意向"]]
            
            selection = st.dataframe(
                grid_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "评分": st.column_config.ProgressColumn(
                        "AI评分", min_value=0, max_value=100, format="%d 分"
                    ),
                    "成交状态": st.column_config.TextColumn("状态", width="small"),
                    "客户意向": st.column_config.TextColumn("意向", width="small"),
                },
                selection_mode="single-row",
                on_select="rerun" # 选中行时自动刷新
            )
            
            # 获取选中行的索引
            selected_rows = selection.selection.rows
            
            st.divider()
            
            # --- 3. 详情透视区 (Deep Dive) ---
            if selected_rows:
                # 获取选中行的数据
                selected_index = selected_rows[0]
                row = df.iloc[selected_index]
                
                st.subheader(f"🔎 深度复盘：{row.get('患者姓名', '未知')}")
                
                # 详情页布局：左侧诊断，右侧证据
                d_col1, d_col2 = st.columns([1, 1], gap="large")
                
                with d_col1:
                    # 头部信息卡
                    with st.container(border=True):
                        c1, c2, c3 = st.columns(3)
                        c1.markdown(f"**咨询师**\n\n{row['咨询师']}")
                        score_color = "green" if row['评分'] >= 80 else "red"
                        c2.markdown(f"**AI评分**\n\n:{score_color}[**{row['评分']}**]")
                        c3.markdown(f"**成交状态**\n\n{row['成交状态']}")
                    
                    # 诊断内容
                    st.markdown("### 🩺 AI 诊断")
                    with st.expander("🎯 客户核心画像", expanded=True):
                        st.markdown(f"**痛点**：{row['痛点']}")
                        st.markdown(f"**意向**：{row['客户意向']}")
                        
                    with st.expander("💡 话术优劣势分析", expanded=True):
                        st.success(f"**做得好的**：\n{row['优点']}")
                        st.error(f"**致命失误**：\n{row['失误点']}")
                        st.info(f"**改进建议**：\n{row['下一步建议']}")

                with d_col2:
                    st.markdown("### 📝 对话实录回放")
                    with st.container(height=600, border=True):
                        # 从数据库读取对话实录
                        chat_log = row.get("对话实录", "无记录")
                        if pd.isna(chat_log) or not str(chat_log).strip():
                            st.warning("⚠️ 该记录未包含对话实录")
                        else:
                            render_dialogue(str(chat_log))
            else:
                st.info("👈 请在上方表格中点击一行，查看详细分析报告。")
                
        else:
            st.empty()
            with st.container():
                st.markdown("""
                <div style='text-align: center; color: #999; padding: 50px;'>
                    <h3>📭 暂无数据</h3>
                    <p>请等待咨询师上传录音文件</p>
                </div>
                """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()