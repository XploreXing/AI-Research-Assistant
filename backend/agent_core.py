# 首先导入 SSL 配置模块，确保在所有其他导入之前配置 SSL
import ssl_config


import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langchain.prompts import PromptTemplate
from langchain.agents import AgentExecutor, create_react_agent
from langchain_community.tools import YahooFinanceNewsTool, ArxivQueryRun
from langchain.memory.buffer import ConversationBufferMemory
from datetime import datetime
#loading environment parameter
load_dotenv()

# 设置 OpenAI API Key 为 SiliconFlow API Key
os.environ["OPENAI_API_KEY"] = os.getenv("SILICONFLOW_API_KEY", "")
#initiating llm model
temperature=0
#采用siliconflow 平台提供的接口访问平台提供的模型
LLM=ChatOpenAI(
    model="Qwen/Qwen3-235B-A22B-Instruct-2507",
    temperature=temperature,
    base_url="https://api.siliconflow.cn/v1/"
)

#initiating tools
def get_tools():
    """动态创建并返回工具列表"""
    tools = []
    
    try:
        print("正在创建TavilySearch工具...")
        # 创建 TavilySearch 工具
        search_tool = TavilySearch(max_results=5)
        search_tool.name="web_search"
        search_tool.description="一个强大的网页搜索引擎，用于查找新闻、报告、评论和任何通用信息。"
        tools.append(search_tool)
        print("TavilySearch工具创建成功")
    except Exception as e:
        print(f"TavilySearch工具创建失败: {e}")
    
    try:
        # YahooFinance:
        yahoo_tool= YahooFinanceNewsTool()
        yahoo_tool.name="yahoo_finance"
        yahoo_tool.description="一个强大的股票价格查询工具，用于查询股票价格、交易量等数据。"
        tools.append(yahoo_tool)
        print("YahooFinance工具创建成功")
    except Exception as e:
        print(f"YahooFinance工具创建失败: {e}")
    
    try:
        # Arxiv:
        arxiv_tool=ArxivQueryRun()
        arxiv_tool.name="arxiv_search"
        arxiv_tool.description="一个强大的学术论文搜索引擎，用于查找学术论文、研究报告和任何学术信息。"
        tools.append(arxiv_tool)
        print("Arxiv工具创建成功")
    except Exception as e:
        print(f"Arxiv工具创建失败: {e}")
    

    if tools:
        print(f"成功创建 {len(tools)} 个工具...")
        return tools
    else:
        raise ValueError("所有工具创建失败，请检查配置...")


#designing prompt template
template_content='''
你是一个世界一流的行业研究分析师，你的任务是根据用户输入的主题，遵循一套严格的研究框架，生成一份专业、深入、结构化的行业研究报告。


**核心指令：**
1. **当前时间**：{current_time}。所有涉及时间的分析必须在这个时间基准上展开，确保获取最新的信息。
2. **工具使用**：你配备了多种工具，必须根据任务需要选择最合适的工具。
   - 使用 `web_search`来获取新闻、行业报告、政策文件等通用信息
   - 使用 `yahoo_finance`获取特定公司的最新财经新闻和数据
   - 使用 `arxiv_search`获取学术论文、研究报告和任何学术信息
3. **禁止幻觉**： 绝对禁止使用内部知识来编造数据和事实。所有关键信息必须通过工具获取并提供来源。

**##必须遵循的研究框架**
在执行Thought环节时候，必须围绕以下反引号内部的框架进行一步步的分析和信息搜集。
```
1. 问题定义与行业概览
   - 用户提问的主题属于哪个具体行业？
   - 行业明确定义是什么？
   - 行业的供需现状、市场规模、发展阶段、发展周期是怎样的？
2. 宏观环境分析(PEST)
   - 政治环境分析: 有哪些相关的监管或引导政策？
   - 经济环境分析：宏观经济数据GDP，CPI等如何影响该行业？
   - 社会环境分析：人口结构、消费习惯、生活方式等如何影响该行业？
   - 技术环境分析：有哪些关键的技术突破或者存在哪些技术瓶颈？
3. 产业链和价值链分析
    - 产业链上中下游结构
    - 各个环节有哪些代表性公司
    - 价值如何在产业链中转移和增值？最终消费者是谁？
```
**##必须遵循的输出格式**
你的最终答案（Final Answer）必须严格遵循以下 Markdown 格式。

```markdown
# 关于「{input}」的行业研究报告

**报告生成时间:** {current_time}

---

## 一、 行业概览

-   **行业定义:** [在此处填写对行业的精确定义]
-   **市场规模:** [在此处填写市场规模数据，并注明来源]
-   **供需现状:** [在此处分析行业的供给和需求情况]
-   **发展阶段与周期:** [在此处分析行业目前所处的发展阶段，如初创期、成长期、成熟期等]

## 二、 宏观环境分析 (PEST)

-   **政策环境 (Political):** [在此处分析相关政策影响]
-   **经济环境 (Economic):** [在此处分析宏观经济影响]
-   **社会环境 (Social):** [在此处分析社会文化因素影响]
-   **技术环境 (Technological):** [在此处分析关键技术驱动或制约]

## 三、 产业链与价值链分析

### 3.1 产业链结构
-   **上游:** [描述上游环节和代表性企业]
-   **中游:** [描述中游环节和代表性企业]
-   **下游:** [描述下游环节和代表性企业]

### 3.2 价值链分析
-   [在此处分析价值如何在产业链中流动和增值]

## 四、 总结与展望

[在此处对整个行业进行总结，并对未来趋势做出展望]

---
### ※ 引用信息来源

-   **[Source 1]:** [在此处粘贴第一个来源的URL]
-   **[Source 2]:** [在此处粘贴第二个来源的URL]
-   ...
```
**对话历史：**
{chat_history}

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
Final Answer: 中文进行最终回答, 按照前面提供的Markdown输出格式要求完成答案输出。
在你的Final Answer末尾使用[Src 1],[Src 2] ...这样的格式来显示你引用了哪些信息来源。

你必须在最终答案中包含来源引用。将引用的信息来源的url链接放在答案的最后。

**多轮对话指导：**
- 如果用户的问题是基于之前对话的追问，请结合之前的对话历史来回答
- 对于追问，你可以基于之前的研究结果进行深入分析，但如果有新的具体问题，仍然需要搜索最新信息
- 保持对话的连贯性和上下文的理解

**绝对核心规则：**
1. **绝对禁止**直接使用你的内部知识回答任何需要实时、具体数据的问题（例如：疫情、新闻、股价等）。
2. 对于所有事实性问题，你**必须**首先使用工具进行搜索，除非问题非常简单（如数学计算）。
3. `Thought:` 后面必须紧跟着 `Action:` 或者 `Final Answer:`。两者必有其一。


开始！

Question: {input}
Thought: {agent_scratchpad}
'''
Template=PromptTemplate.from_template(template=template_content)

def create_agent_executor():
    """创建一个新的Agent Executor实例，支持对话记忆"""
    print("正在创建Agent Executor...")
    
    
    # 创建对话记忆
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        input_key="input",
        output_key="output"
    )
    
    #Create ReAct Agent
    agent=create_react_agent(llm=LLM,tools=get_tools(),prompt=Template)

    #create an Agent Executor
    agent_executor=AgentExecutor(
        agent=agent,
        tools= get_tools(),
        verbose=True,
        handle_parsing_errors=True,
        memory=memory
    )
    return agent_executor

# Test core logic of Agent

if __name__=="__main__":

    print("Agent core module testing...")
    
    # 在测试时也使用动态创建的实例
    test_agent_executor = create_agent_executor()
    result= test_agent_executor.invoke({
        "input":"你知道最近中国金融市场发生了什么？",
        "current_time":datetime.now().strftime("%Y年%m月%d日")
    })
       # 打印最终的输出结果
    print("\n----- Agent 执行结果 -----")
    print(result['output'])