# 首先导入 SSL 配置模块，确保在所有其他导入之前配置 SSL
from ssl_config import configure_ssl

import gradio as gr
from datetime import datetime
from agent_core import create_agent_executor

print('Gradio 应用启动中...')

# 在应用启动时创建一个Agent Executor实例
# 这确保了它在Gradio的事件循环中被正确初始化
agent_executor_instance = create_agent_executor()
# ssl_config.configure_ssl()

async def research_interface(topic):
    if not topic:
        return "错误：请输入一个研究问题"
    
    print(f"当前的研究任务是：{topic}")

    current_time=datetime.now().strftime("%Y年%m月%d日")

    try:
        # 确保在异步环境中 SSL 配置正确
        # ssl_config.configure_async_ssl()
        
        # 使用动态创建的Agent Executor实例
        response = await agent_executor_instance.ainvoke({
            "input":topic,
            "current_time":current_time
        })
        return response.get("output", "没有获取到有效响应")
    except Exception as e:
        print(f"Agent 执行中发生错误: {e}")
        error_msg = f"Agent 执行中发生错误: {str(e)}"
        if "SSL" in str(e) or "certificate" in str(e).lower():
            error_msg += "\n\n这可能是 SSL 证书验证问题。请检查网络连接或联系管理员。"
        return error_msg
    

iface=gr.Interface(
    fn=research_interface,
    inputs=gr.Textbox(lines=2, placeholder="例如：什么是RAG系统"),
    outputs=gr.Textbox(label="研究结果"),
    title="智能研究助手(Gradio)",
    description="输入一个主题，AI 将为你进行研究、总结并提供来源。由 Gradio 驱动。",
    examples=[ # 提供一些示例，方便用户点击试用
        ["量子计算的最新突破"],
        ["大语言模型在教育领域的应用前景"],
    ]
)

if __name__=="__main__":
    # 启动时使用自定义的 SSL 配置
    iface.launch()