"""
对话管理器 - 负责多轮对话的状态管理、性能优化和异常处理
"""

import json
import asyncio
from datetime import datetime
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass, asdict
import logging
from contextlib import asynccontextmanager
import time

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ConversationTurn:
    """单轮对话的数据结构"""
    user_message: str
    ai_response: str
    timestamp: str
    turn_number: int
    processing_time: float
    error_occurred: bool = False
    error_message: str = ""

@dataclass
class ConversationSession:
    """对话会话的数据结构"""
    session_id: str
    created_at: str
    turns: List[ConversationTurn]
    total_tokens: int = 0
    last_activity: str = ""
    
    def to_dict(self):
        return asdict(self)

class ConversationManager:
    """对话管理器 - 负责多轮对话的状态管理和优化"""
    
    def __init__(self, max_history_length: int = 10, max_session_age_hours: int = 24):
        self.max_history_length = max_history_length
        self.max_session_age_hours = max_session_age_hours
        self.sessions: Dict[str, ConversationSession] = {}
        self.active_session_id: Optional[str] = None
        
    def create_session(self) -> str:
        """创建新的对话会话"""
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{id(self)}"
        self.sessions[session_id] = ConversationSession(
            session_id=session_id,
            created_at=datetime.now().isoformat(),
            turns=[],
            last_activity=datetime.now().isoformat()
        )
        self.active_session_id = session_id
        logger.info(f"创建新会话: {session_id}")
        return session_id
    
    def get_active_session(self) -> Optional[ConversationSession]:
        """获取当前活跃会话"""
        if self.active_session_id and self.active_session_id in self.sessions:
            return self.sessions[self.active_session_id]
        return None
    
    def add_turn(self, user_message: str, ai_response: str, processing_time: float, 
                 error_occurred: bool = False, error_message: str = "") -> bool:
        """添加一轮对话"""
        session = self.get_active_session()
        if not session:
            logger.warning("没有活跃会话，无法添加对话轮次")
            return False
        
        # 检查会话是否过期
        if self._is_session_expired(session):
            logger.info(f"会话 {session.session_id} 已过期，创建新会话")
            self.create_session()
            session = self.get_active_session()
        
        # 创建新的对话轮次
        turn = ConversationTurn(
            user_message=user_message,
            ai_response=ai_response,
            timestamp=datetime.now().isoformat(),
            turn_number=len(session.turns) + 1,
            processing_time=processing_time,
            error_occurred=error_occurred,
            error_message=error_message
        )
        
        # 添加到会话中
        session.turns.append(turn)
        session.last_activity = datetime.now().isoformat()
        
        # 如果超过最大历史长度，移除最早的对话
        if len(session.turns) > self.max_history_length:
            session.turns.pop(0)
            logger.info(f"会话 {session.session_id} 达到最大历史长度，移除最早对话")
        
        logger.info(f"添加对话轮次到会话 {session.session_id}: 轮次 {turn.turn_number}")
        return True
    
    def get_conversation_history(self) -> List[Tuple[str, str]]:
        """获取对话历史，格式化为 (用户消息, AI回复) 的元组列表"""
        session = self.get_active_session()
        if not session:
            return []
        
        return [(turn.user_message, turn.ai_response) for turn in session.turns]
    
    def get_formatted_history(self) -> str:
        """获取格式化的对话历史用于显示"""
        session = self.get_active_session()
        if not session or not session.turns:
            return "暂无对话历史"
        
        formatted_history = f"**会话ID:** {session.session_id}\n"
        formatted_history += f"**创建时间:** {session.created_at}\n"
        formatted_history += f"**总轮次:** {len(session.turns)}\n\n"
        
        for turn in session.turns:
            formatted_history += f"**第{turn.turn_number}轮对话：**\n"
            formatted_history += f"**用户：** {turn.user_message}\n"
            formatted_history += f"**AI助手：** {turn.ai_response}\n"
            if turn.error_occurred:
                formatted_history += f"**⚠️ 错误：** {turn.error_message}\n"
            # 确保processing_time不为None
            processing_time_display = turn.processing_time if turn.processing_time is not None else 0.0
            formatted_history += f"**处理时间：** {processing_time_display:.2f}秒\n"
            formatted_history += "---\n\n"
        
        return formatted_history
    
    def clear_session(self) -> bool:
        """清空当前会话"""
        if self.active_session_id:
            del self.sessions[self.active_session_id]
            self.active_session_id = None
            logger.info("当前会话已清空")
            return True
        return False
    
    def export_session(self, filepath: Optional[str] = None) -> str:
        """导出当前会话"""
        session = self.get_active_session()
        if not session:
            return "暂无会话可导出"
        
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "session": session.to_dict()
        }
        
        try:
            if not filepath:
                filepath = f"conversation_export_{session.session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"会话已导出到: {filepath}")
            return f"会话已导出到文件：{filepath}"
        except Exception as e:
            error_msg = f"导出失败：{str(e)}"
            logger.error(error_msg)
            return error_msg
    
    def _is_session_expired(self, session: ConversationSession) -> bool:
        """检查会话是否过期"""
        try:
            created_time = datetime.fromisoformat(session.created_at)
            current_time = datetime.now()
            age_hours = (current_time - created_time).total_seconds() / 3600
            return age_hours > self.max_session_age_hours
        except Exception as e:
            logger.error(f"检查会话过期时出错: {e}")
            return False
    
    def cleanup_expired_sessions(self) -> int:
        """清理过期的会话"""
        expired_sessions = []
        for session_id, session in self.sessions.items():
            if self._is_session_expired(session):
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
            if session_id == self.active_session_id:
                self.active_session_id = None
        
        logger.info(f"清理了 {len(expired_sessions)} 个过期会话")
        return len(expired_sessions)

@asynccontextmanager
async def conversation_timer():
    """异步上下文管理器，用于计时对话处理时间"""
    start_time = time.time()
    try:
        yield
    finally:
        processing_time = time.time() - start_time
        logger.info(f"对话处理耗时: {processing_time:.2f}秒")

class ConversationError(Exception):
    """对话相关错误的基类"""
    pass

class SessionNotFoundError(ConversationError):
    """会话未找到错误"""
    pass

class ConversationLimitError(ConversationError):
    """对话限制错误"""
    pass 