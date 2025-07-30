# 首先导入 SSL 配置模块，确保在所有其他导入之前配置 SSL
from ssl_config import configure_ssl

import gradio as gr
from datetime import datetime
from agent_core import create_agent_executor
from conversation_manager import ConversationManager, ConversationError
import asyncio
import logging
import time # Added for time.time()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print('Gradio 应用启动中...')

# 全局对话管理器
conversation_manager = ConversationManager(max_history_length=15, max_session_age_hours=48)

# 全局Agent实例
agent_executor_instance = None

def initialize_agent():
    """初始化Agent Executor"""
    global agent_executor_instance
    if agent_executor_instance is None:
        logger.info("初始化Agent Executor...")
        agent_executor_instance = create_agent_executor()
    return agent_executor_instance

def ensure_session_exists():
    """确保存在活跃会话"""
    if not conversation_manager.get_active_session():
        conversation_manager.create_session()
        logger.info("创建新会话")

async def research_interface(topic, is_follow_up=False):
    """主要研究接口，支持初始问题和追问"""
    if not topic:
        return "错误：请输入一个研究问题", conversation_manager.get_formatted_history()
    
    logger.info(f"处理研究任务: {topic}, 是否为追问: {is_follow_up}")
    
    # 确保会话存在
    ensure_session_exists()
    
    current_time = datetime.now().strftime("%Y年%m月%d日")
    processing_time = 0.0  # 确保是float类型
    error_occurred = False
    error_message = ""
    ai_response = ""

    # 记录开始时间
    start_time = time.time()
    
    try:
        # 确保Agent已初始化
        agent_executor = initialize_agent()
        
        # 使用动态创建的Agent Executor实例
        response = await agent_executor.ainvoke({
            "input": topic,
            "current_time": current_time
        })
        
        ai_response = response.get("output", "没有获取到有效响应")
        
    except Exception as e:
        error_occurred = True
        error_message = str(e)
        logger.error(f"Agent 执行中发生错误: {e}")
        
        if "SSL" in str(e) or "certificate" in str(e).lower():
            ai_response = f"Agent 执行中发生错误: {str(e)}\n\n这可能是 SSL 证书验证问题。请检查网络连接或联系管理员。"
        else:
            ai_response = f"Agent 执行中发生错误: {str(e)}"
    
    finally:
        # 计算处理时间
        processing_time = time.time() - start_time
        logger.info(f"对话处理耗时: {processing_time:.2f}秒")
    
    # 添加对话轮次到管理器
    conversation_manager.add_turn(
        user_message=topic,
        ai_response=ai_response,
        processing_time=processing_time,
        error_occurred=error_occurred,
        error_message=error_message
    )
    
    # 返回结果和更新的对话历史
    return ai_response, conversation_manager.get_formatted_history()

async def follow_up_question(follow_up_topic):
    """处理追问的专门函数"""
    if not follow_up_topic:
        return "错误：请输入追问内容", conversation_manager.get_formatted_history()
    
    # 检查是否有对话历史
    if not conversation_manager.get_active_session() or not conversation_manager.get_active_session().turns:
        return "错误：请先进行初始研究，然后再进行追问", conversation_manager.get_formatted_history()
    
    return await research_interface(follow_up_topic, is_follow_up=True)

def clear_conversation():
    """清空对话历史"""
    conversation_manager.clear_session()
    # 重新初始化Agent以清空记忆
    global agent_executor_instance
    agent_executor_instance = None
    logger.info("对话历史已清空，Agent已重新初始化")
    return "对话历史已清空", "暂无对话历史"

def export_conversation():
    """导出对话历史"""
    return conversation_manager.export_session()

def get_conversation_stats():
    """获取对话统计信息"""
    session = conversation_manager.get_active_session()
    if not session:
        return "暂无活跃会话"
    
    stats = f"**会话统计信息：**\n"
    stats += f"会话ID: {session.session_id}\n"
    stats += f"创建时间: {session.created_at}\n"
    stats += f"总轮次: {len(session.turns)}\n"
    stats += f"最后活动: {session.last_activity}\n"
    
    if session.turns:
        # 确保processing_time不为None，如果为None则视为0.0
        valid_times = [turn.processing_time if turn.processing_time is not None else 0.0 for turn in session.turns]
        total_time = sum(valid_times)
        avg_time = total_time / len(session.turns)
        stats += f"总处理时间: {total_time:.2f}秒\n"
        stats += f"平均处理时间: {avg_time:.2f}秒\n"
        
        error_count = sum(1 for turn in session.turns if turn.error_occurred)
        if error_count > 0:
            stats += f"错误轮次: {error_count}\n"
    
    return stats

# 创建Gradio界面
with gr.Blocks(title="智能研究助手 - 多轮对话版", theme=gr.themes.Soft()) as iface:
    gr.Markdown("# 🔬 智能研究助手 - 多轮对话版")
    gr.Markdown("输入一个主题，AI 将为你进行研究、总结并提供来源。支持多轮深度对话！")
    
    with gr.Row():
        with gr.Column(scale=2):
            # 主要研究区域
            gr.Markdown("## 📝 初始研究问题")
            main_input = gr.Textbox(
                lines=3, 
                placeholder="例如：什么是RAG系统？请详细解释其工作原理和应用场景。",
                label="研究问题"
            )
            main_submit_btn = gr.Button("🔍 开始研究", variant="primary")
            main_output = gr.Textbox(
                label="研究结果", 
                lines=8,
                interactive=False
            )
            
            # 追问区域
            gr.Markdown("## 💭 继续追问")
            follow_up_input = gr.Textbox(
                lines=2, 
                placeholder="例如：RAG系统与传统搜索引擎有什么区别？",
                label="追问内容"
            )
            follow_up_btn = gr.Button("❓ 继续追问", variant="secondary")
            follow_up_output = gr.Textbox(
                label="追问回答", 
                lines=6,
                interactive=False
            )
            
            # 控制按钮
            with gr.Row():
                clear_btn = gr.Button("🗑️ 清空对话", variant="stop")
                export_btn = gr.Button("📤 导出对话", variant="secondary")
                stats_btn = gr.Button("📊 对话统计", variant="secondary")
            
            export_result = gr.Textbox(label="操作结果", interactive=False)
        
        with gr.Column(scale=1):
            # 对话历史显示区域
            gr.Markdown("## 📚 对话历史")
            history_display = gr.Markdown(
                value="暂无对话历史",
                label="对话记录"
            )
            
            # 示例问题
            gr.Markdown("## 💡 示例问题")
            gr.Examples(
                examples=[
                    ["量子计算的最新突破和应用前景"],
                    ["大语言模型在教育领域的应用前景"],
                    ["人工智能在医疗诊断中的最新进展"],
                ],
                inputs=main_input
            )
    
    # 事件绑定
    main_submit_btn.click(
        fn=research_interface,
        inputs=[main_input],
        outputs=[main_output, history_display]
    )
    
    follow_up_btn.click(
        fn=follow_up_question,
        inputs=[follow_up_input],
        outputs=[follow_up_output, history_display]
    )
    
    clear_btn.click(
        fn=clear_conversation,
        inputs=[],
        outputs=[main_output, history_display]
    )
    
    export_btn.click(
        fn=export_conversation,
        inputs=[],
        outputs=[export_result]
    )
    
    stats_btn.click(
        fn=get_conversation_stats,
        inputs=[],
        outputs=[export_result]
    )

if __name__=="__main__":
    # 启动时使用自定义的 SSL 配置
    iface.launch()