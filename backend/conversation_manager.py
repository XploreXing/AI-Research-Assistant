from dataclasses import dataclass,asdict
from datetime import datetime
from typing import List,Tuple,Dict,Optional
import uuid
import time
import logging
import json
from pathlib import Path
import sys

backend_root=Path(__file__).resolve().parent

data_dir=backend_root/'data'
data_dir.mkdir(parents=True,exist_ok=True)

sys.path.insert(0,str(backend_root))

logging.basicConfig(level=logging.INFO)
logger=logging.getLogger(__name__)



@dataclass
class SingleConversation:
    """单轮对话数据结构定义"""
    user_query:str
    ai_response:str
    timestamp:str
    turn_number:int
    processing_time:float
    error_occurred:bool=False
    error_message:str=''

    def to_dict(self):
        return asdict(self)
    
@dataclass
class ConversationSession:
    """对话会话数据结构定义"""
    session_id:str
    created_at:str
    turns:List[SingleConversation]
    total_tokens:int=0
    last_activity:str=''

    def to_dict(self):
        return asdict(self)
    
class ConversationManager:
    def __init__(self,max_history_length:int=10, max_session_age_hours:int=12):
        self.max_history_length=max_history_length
        self.max_session_age_hours=max_session_age_hours
        self.sessions:Dict[str,ConversationSession]={}
        self.active_session_id:Optional[str]=None
    def create_session(self)->str:

        session_id=f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4()}"
        self.sessions[session_id]=ConversationSession(
            session_id=session_id,
            created_at=datetime.now().isoformat(),
            turns=[],
            last_activity=datetime.now().isoformat(),
        ) #ConversationManager中管理的sessions是一个字典，通过session_id获取对应的session，而session对象中的turns字段包含了所有的单次对话历史
        self.active_session_id=session_id
        logger.info(f"创建新会话：{session_id}")
        return session_id
   
    def add_chat_history(self,last_single_conversation:SingleConversation)->bool:
        if not self.active_session_id:
            logger.warning("没有活跃会话，无法添加对话轮次")
            return False
        session=self.sessions[self.active_session_id]
        if self.is_session_expired(session):
            logger.warning("会话已过期，创建新会话")

            self.create_session()
            session=self.sessions[self.active_session_id]
        session.turns.append(last_single_conversation)
        session.last_activity=datetime.now().isoformat()
        
        if len(session.turns)>self.max_history_length:
            session.turns.pop(0) #这个操作其实是O(n)的，但是因为会话轮次不会太多，所以可以接受
            logger.info(f"会话{session.session_id}达到最大历史长度，移除最早对话")
        logger.info(f"添加对话轮次：{last_single_conversation.turn_number}")

        return True
    
    def format_single_chat_history(self,user_query:str,ai_response:str,error_occurred:bool=False,processing_time:float=0,error_message:str='')->SingleConversation:
        session = self.sessions.get(self.active_session_id)
        if not session:
            raise ValueError("没有活跃会话")
        return SingleConversation(
            user_query=user_query,
            ai_response=ai_response,
            timestamp=datetime.now().isoformat(),
            turn_number=len(session.turns)+1,
            processing_time=processing_time,
            error_occurred=error_occurred,
            error_message=error_message
        )
    def get_active_session(self):
        if self.active_session_id and self.active_session_id in self.sessions:
           return self.sessions.get(self.active_session_id)
        return None
    
    def get_conversaion_history(self)->List[Tuple[str,str]]:
        """返回当前调用之前的所有对话历史，格式化为(用户消息,AI回复)的元组列表"""
        session=self.get_active_session()
        if not session:
            return []
        return [(turn.user_query,turn.ai_response) for turn in session.turns]
    
    def get_formatted_history(self)->str:
        """返回当前调用之前的所有对话历史用于显示到gradio前端"""
        session=self.get_active_session()
        if not session or not session.turns:
            return "暂无对话历史"
        
        formatted_history=f'**会话ID:** {session.session_id}\n'
        formatted_history+=f"**创建时间:** {session.created_at}\n"
        formatted_history+=f"**总轮次:** {len(session.turns)}\n\n"
        conversation_history=self.get_conversaion_history()
        for index,turn in enumerate(conversation_history):
            formatted_history+=f"**第{index+1}轮对话:**\n"
            formatted_history+=f"**用户:**{turn[0]}\n"
            ai_response = turn[1]
            ai_response = ai_response.replace('[Source', '<small>[Source')
            ai_response = ai_response.replace(']', ']</small>')
            
            formatted_history+=f"**AI助手:** {ai_response}\n"
            formatted_history+="---\n\n"
        return formatted_history
    
    def clear_session(self):
        if self.active_session_id:
            del self.sessions[self.active_session_id]
            self.active_session_id=None
            logger.info("当前会话已清空")
            return True
        return False
    def export_session(self,filepath:Optional[str]=None)->str:
        session=self.get_active_session()
        if not session:
            return "没有活跃会话，无法导出"
        if not filepath:
            filepath=f"conversation_export_{session.session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        # 设定文件路径
        
        with open(data_dir/filepath,'w', encoding='utf-8') as f:
            json.dump(session.to_dict(),f,indent=4,ensure_ascii=False)
        logger.info(f"会话已导出到：{filepath}")
        return f"会话已导出到文件：{filepath}"

    def is_session_expired(self,session:ConversationSession)->bool:

        #当前时间-创建时间 是否超过 max_session_age_hours
        created_time=datetime.fromisoformat(session.created_at)
        current_time=datetime.now()
        duration=(current_time-created_time).total_seconds()/3600
        return duration>self.max_session_age_hours
    
    def cleanup_expired_sessions(self)->int:
        expired_session_ids=[]

        for session_id,session in self.sessions.items():
            if self.is_session_expired(session):
                expired_session_ids.append(session_id)
        for session_id in expired_session_ids:
            del self.sessions[session_id]
            if session_id==self.active_session_id: #同步更新
                self.active_session_id=None
        num_expired=len(expired_session_ids)
        logger.info(f"清理了{num_expired}个过期会话")

        return num_expired
    
class ConversationTimer:
    def __init__(self):
        self.start_time=0
        self.duration=0
    async def __aenter__(self):
        """进入async with模块时使用"""
        logger.info("开始计时...")
        self.start_time=time.perf_counter()
        return self
    async def __aexit__(self,exc_type,exc_value,traceback):
        """退出async with模块时使用"""
        self.duration=time.perf_counter()-self.start_time
        logger.info(f"对话处理耗时: {self.duration:.2f}秒")
        return self.duration
