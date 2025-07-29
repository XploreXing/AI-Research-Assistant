# 首先导入 SSL 配置模块，确保在所有其他导入之前配置 SSL
import ssl_config


import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langchain.prompts import PromptTemplate
from langchain.agents import AgentExecutor, create_react_agent

from datetime import datetime
#loading environment parameter
load_dotenv()

# 设置 OpenAI API Key 为 SiliconFlow API Key
os.environ["OPENAI_API_KEY"] = os.getenv("SILICONFLOW_API_KEY", "")

#initiating llm model
temparature=0
#采用siliconflow 平台提供的接口访问平台提供的模型
LLM=ChatOpenAI(
    model="Qwen/Qwen3-235B-A22B-Instruct-2507",
    temperature=temparature,
    base_url="https://api.siliconflow.cn/v1/"
)

#initiating tools
def get_tools():
    """动态创建并返回工具列表"""
    print("正在创建TavilySearch工具...")
    
    # # 确保在创建工具时 SSL 配置已经生效
    # ssl_config.configure_ssl()
    
    # 创建 TavilySearch 工具
    search_tool = TavilySearch(max_results=3)
    
    return [search_tool]

#designing prompt template
template_content='''
你是一个世界一流的研究助手，你的任务是可以使用可用的工具来回答用户提出的研究问题。

**重要上下文：**
今天是：**{current_time}**。你必须利用这个信息来构建搜索查询，确保获取最新的信息。

你需要为你的最终答案提供信息来源，最终答案应该是对研究问题的全面总结。
你可以使用的工具：{tools}
使用以下格式：

Question: 你必须回答的输入问题。
Thought: 你应该在接收到问题后，总是首先思考应该怎么解决这个问题，从时间，动作主体，动作等框架拆分，涉及时间点，务必根据{current_time}进行时间判断。
Action: 【如果决定使用工具】要采取的行动，来源于[{tool_names}]中的一个工具。
Action Input: 【如果决定使用工具】动作的输入。
Observation：【如果决定使用工具】动作的结果。
... (这个 Thought/Action/Action Input/Observation的过程可以多次重复)

Thought: 【如果决定不再使用工具或已经有足够信息】我现在知道最终答案了。
Final Answer: 对于原始的输入问题用中文进行最终回答，并包含引用的信息来源。
在你的Final Answer末尾使用[Source 1],[Source 2] ...这样的格式来显示你引用了哪些信息来源。

你必须在最终答案中包含来源引用。将引用的信息来源的url链接放在答案的最后。
**绝对核心规则：**
1. **绝对禁止**直接使用你的内部知识回答任何需要实时、具体数据的问题（例如：疫情、新闻、股价等）。
2. 对于所有事实性问题，你**必须**首先使用工具进行搜索，除非问题非常简单（如数学计算）。
3. `Thought:` 后面必须紧跟着 `Action:` 或者 `Final Answer:`。两者必有其一。
4. 在你的 `Final Answer` 的末尾，使用 [Source 1], [Source 2] ... 的格式来引用信息来源。

开始！

Question: {input}
Thought: {agent_scratchpad}
'''
Template=PromptTemplate.from_template(template=template_content)

def create_agent_executor():
    """创建一个新的Agent Executor实例"""
    print("正在创建Agent Executor...")
    #Create ReAct Agent
    agent=create_react_agent(llm=LLM,tools=get_tools(),prompt=Template)

    #create an Agent Executor
    agent_executor=AgentExecutor(
        agent=agent,
        tools= get_tools(),
        verbose=True,
        handle_parsing_errors=True
    )
    return agent_executor

# 为了兼容旧的导入方式，我们仍然可以导出一个实例，但这不再是推荐的方式
agent_executor = create_agent_executor()

# Test core logic of Agent

if __name__=="__main__":

    print("Agent core module testing...")
    
    # 在测试时也使用动态创建的实例
    test_agent_executor = create_agent_executor()
    result= test_agent_executor.invoke({
        "input":"你知道释永信最近为什么被抓吗？",
        "current_time":datetime.now().strftime("%Y年%m月%d日")
    })
       # 打印最终的输出结果
    print("\n----- Agent 执行结果 -----")
    print(result['output'])