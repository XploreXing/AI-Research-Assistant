from ssl_config import configure_ssl

import gradio as gr
from datetime import datetime
from agent_core import create_agent_executor
from conversation_manager_manual import ConversationManager,ConversationTimer
import logging

#Configure SSL
logging.basicConfig(level=logging.INFO)
logger=logging.getLogger(__name__)

#Configure Global Conversation Manager
conversation_manager=ConversationManager(max_history_length=5,max_session_age_hours=12)

#Initialize agent instance

agent_executor_instance=None

def initialize_agent():
    """Initialize Agent Executor"""
    global agent_executor_instance #clarify the global variable
    if agent_executor_instance is None:
        logger.info("Initializing Agent Executor...")
        agent_executor_instance=create_agent_executor()
    return agent_executor_instance

def ensure_session_exists():
    if not conversation_manager.get_active_session():
        logger.info("Creating New Session...")
        new_session=conversation_manager.create_session()
        if new_session:
            logger.info(f"Created New Session: {new_session}")
        else:
            logger.error("Failed to Create New Session")


#定义gradio中要用到的接口函数
async def research_interface(topic, is_follow_up=False):#默认初始问题而非追问
    if not topic:
        return "Error: please enter a research topic",conversation_manager.get_formatted_history()
    
    ensure_session_exists() #如果没有会话 这个函数会创建一个新会话

    current_time=datetime.now().strftime("%Y年%m月%d日")
    error_occurred=False
    error_message=""
    ai_response=""
    
    TIMER=ConversationTimer()
    try:
        async with TIMER:
            agent_executor=initialize_agent()
            response=await agent_executor.ainvoke({
                "input":topic,
                "current_time":current_time
            })
            ai_response=response.get("output","No valid response")
           
    except Exception as e:
        error_occurred=True
        error_message=str(e)
        logger.error(f"Error in research interface: {e}")

    #准备构建SingleConversation对象
    single_conversation=conversation_manager.format_single_chat_history(
        user_query=topic,
        ai_response=ai_response,
        processing_time=TIMER.duration,
        error_occurred=error_occurred,
        error_message=error_message
    )

    #添加到会话中
    conversation_manager.add_chat_history(single_conversation)

    #返回结果和更新的对话历史
    return ai_response,conversation_manager.get_formatted_history()

#定义追问的接口函数
async def follow_up_question(follow_up_topic:str):
    if not follow_up_topic:
        return "Error: please enter a follow-up question",conversation_manager.get_formatted_history()
    
    #检查是否有对话历史
    if not conversation_manager.get_active_session() or not conversation_manager.get_active_session().turns:
        return "Error: please start an initial research first",conversation_manager.get_formatted_history()
    
    return await research_interface(follow_up_topic, is_follow_up=True)

    
#定义几个按钮函数 清空对话， 导出对话， 获取对话统计

def clear_conversation():
    conversation_manager.clear_session()

    global agent_executor_instance
    agent_executor_instance=None
    logger.info("Conversation Cleared")
    return "Conversation Cleared",conversation_manager.get_formatted_history()


def export_conversation():
    return conversation_manager.export_session()

def get_conversation_stats():
    session=conversation_manager.get_active_session()
    if not session:
        return "No active session"
    stats=f"**会话统计信息**\n"
    stats+=f"会话ID: {session.session_id}\n"
    stats+=f"创建时间: {session.created_at}\n"
    stats+=f"总轮次: {len(session.turns)}\n"
    stats+=f"最后活动: {session.last_activity}\n"

    if session.turns:
        valid_times=[turn.processing_time if turn.processing_time is not None else 0.0 for turn in session.turns]
        total_time=sum(valid_times)
        avg_time=total_time/len(session.turns)
        stats+=f"总处理时间: {total_time:.2f}秒\n"
        stats+=f"平均处理时间: {avg_time:.2f}秒\n"

        error_count=sum(1 for turn in session.turns if turn.error_occurred)
        if error_count>0:
            stats+=f"错误轮次: {error_count}\n"
    return stats

#定义gradio界面
with gr.Blocks(title="AI research assistant - multiturn conversation",theme=gr.themes.Glass()) as iface:
    gr.Markdown("# 🔬 AI研究助手 - 多轮对话版")
    gr.Markdown("### ✍️ 输入一个你感兴趣的研究主题, AI将使用网络材料协助你探索并提供总结。支持多轮对话！")
    with gr.Row():
        with gr.Column(scale=3): #通过with gr.Row() with gr.Column 框定区域
            gr.Markdown("## 🧠 初始研究问题")
            main_input=gr.Textbox(
                lines=4,
                placeholder="例如：什么是RAG系统？请详细解释其工作原理和应用场景。",
                label="探究问题"

            )
            main_submit_btn=gr.Button("🔍 开始研究",variant="primary")#variant 是按钮的样式
            main_output=gr.Textbox(
                label="研究结果",
                lines=10,
                interactive=False
            )

            #追问区域
            gr.Markdown("## 🔍 继续追问")
            followup_input=gr.Textbox(
                label="追问内容",
                lines=4,
                placeholder="例如：请进一步解释RAG系统的当前面临挑战",
            )
            followup_btn=gr.Button(" ❓追问",variant="secondary")
            followup_output=gr.Textbox(
                label="追问回答",
                lines=10,
                interactive=False
            )
            #控制按钮
            with gr.Row():
                clear_btn=gr.Button("🧹清空对话",variant="secondary")
                export_btn=gr.Button("🫗 导出对话",variant="secondary")
                stats_btn=gr.Button("📊 对话统计",variant="secondary")

            export_result=gr.Textbox(label="操作结果",interactive=False)

        with gr.Column(scale=1):

                gr.Markdown("## 📖 对话历史")
                history_display=gr.Markdown(
                    value="暂无对话历史",
                    label="对话记录"
                )

                gr.Markdown("## 💡 示例问题")
                gr.Examples(
                    examples=[
                        ["中国当前金融市场情况如何"],
                        ["AI在翻译领域的应用前景"],
                        ["量子计算在当前的最新进展"],
                    ],
                    inputs=main_input
                )
            #event 绑定
        main_submit_btn.click(
                fn=research_interface, #点击后调用的函数
                inputs=[main_input],
                outputs=[main_output,history_display]
            )
        followup_btn.click(
                fn=follow_up_question,
                inputs=[followup_input],
                outputs=[followup_output,history_display]
            )
        clear_btn.click(
                fn=clear_conversation,
                inputs=[],
                outputs=[main_output,followup_output,history_display]#指定的是fn函数的输出结果的显示位置
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
    iface.queue()
    iface.launch()