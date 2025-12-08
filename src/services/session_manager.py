"""
会话管理模块

提供会话的创建、保存、加载、删除和重命名功能。
"""

import os
import json
import uuid
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class Message:
    """消息数据类"""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: str
    sequence_number: int
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)
    
    @staticmethod
    def from_dict(data: Dict) -> 'Message':
        """从字典创建消息对象"""
        return Message(**data)


@dataclass
class Session:
    """会话数据类"""
    session_id: str
    name: str
    messages: List[Message] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        data = asdict(self)
        # 转换消息列表
        data['messages'] = [msg.to_dict() if isinstance(msg, Message) else msg 
                           for msg in self.messages]
        return data
    
    @staticmethod
    def from_dict(data: Dict) -> 'Session':
        """从字典创建会话对象"""
        # 转换消息列表
        messages = [Message.from_dict(msg) if isinstance(msg, dict) else msg 
                   for msg in data.get('messages', [])]
        
        return Session(
            session_id=data['session_id'],
            name=data['name'],
            messages=messages,
            created_at=data.get('created_at', datetime.now().isoformat()),
            updated_at=data.get('updated_at', datetime.now().isoformat()),
            metadata=data.get('metadata', {})
        )
    
    def add_message(self, role: str, content: str) -> Message:
        """
        添加消息到会话
        
        Args:
            role: 消息角色 ('user' or 'assistant')
            content: 消息内容
            
        Returns:
            Message: 创建的消息对象
        """
        sequence_number = len(self.messages)
        message = Message(
            role=role,
            content=content,
            timestamp=datetime.now().isoformat(),
            sequence_number=sequence_number
        )
        self.messages.append(message)
        self.updated_at = datetime.now().isoformat()
        return message
    
    def get_latest_message_preview(self, max_length: int = 50) -> str:
        """
        获取最新消息预览
        
        Args:
            max_length: 最大预览长度
            
        Returns:
            str: 消息预览文本
        """
        if not self.messages:
            return "暂无消息"
        
        latest_msg = self.messages[-1]
        content = latest_msg.content
        
        # 截断长消息
        if len(content) > max_length:
            content = content[:max_length] + "..."
        
        return content


class SessionManager:
    """会话管理器"""
    
    def __init__(self, storage_path: str = "./sessions", auto_save: bool = True):
        """
        初始化会话管理器
        
        Args:
            storage_path: 会话存储路径
            auto_save: 是否启用自动保存
        """
        self.storage_path = Path(storage_path)
        self.auto_save = auto_save
        self.current_session: Optional[Session] = None
        
        # 确保存储目录存在
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"SessionManager 初始化完成，存储路径: {self.storage_path}")
    
    def create_session(self, name: Optional[str] = None) -> Session:
        """
        创建新会话
        
        Args:
            name: 会话名称，如果为 None 则自动生成
            
        Returns:
            Session: 创建的会话对象
        """
        # 生成唯一的会话 ID
        session_id = str(uuid.uuid4())
        
        # 如果没有提供名称，使用默认名称
        if name is None:
            name = f"新会话 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # 创建会话对象
        session = Session(
            session_id=session_id,
            name=name
        )
        
        # 创建会话目录
        session_dir = self.storage_path / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存会话
        self.save_session(session)
        
        # 设置为当前会话
        self.current_session = session
        
        logger.info(f"创建新会话: {session_id} - {name}")
        
        return session
    
    def save_session(self, session: Session) -> None:
        """
        保存会话到磁盘
        
        Args:
            session: 要保存的会话对象
        """
        try:
            session_dir = self.storage_path / session.session_id
            session_dir.mkdir(parents=True, exist_ok=True)
            
            # 更新时间戳
            session.updated_at = datetime.now().isoformat()
            
            # 保存元数据
            metadata_path = session_dir / "metadata.json"
            metadata = {
                'session_id': session.session_id,
                'name': session.name,
                'created_at': session.created_at,
                'updated_at': session.updated_at,
                'message_count': len(session.messages),
                'metadata': session.metadata
            }
            
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            # 保存消息历史
            messages_path = session_dir / "messages.json"
            messages_data = [msg.to_dict() for msg in session.messages]
            
            with open(messages_path, 'w', encoding='utf-8') as f:
                json.dump(messages_data, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"会话已保存: {session.session_id}")
            
        except Exception as e:
            logger.error(f"保存会话失败: {session.session_id}, 错误: {e}", exc_info=True)
            raise
    
    def load_session(self, session_id: str) -> Session:
        """
        加载会话
        
        Args:
            session_id: 会话 ID
            
        Returns:
            Session: 加载的会话对象
            
        Raises:
            FileNotFoundError: 会话不存在
            ValueError: 会话文件损坏
        """
        try:
            session_dir = self.storage_path / session_id
            
            if not session_dir.exists():
                raise FileNotFoundError(f"会话不存在: {session_id}")
            
            # 加载元数据
            metadata_path = session_dir / "metadata.json"
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # 加载消息历史
            messages_path = session_dir / "messages.json"
            messages = []
            if messages_path.exists():
                with open(messages_path, 'r', encoding='utf-8') as f:
                    messages_data = json.load(f)
                    messages = [Message.from_dict(msg) for msg in messages_data]
            
            # 创建会话对象
            session = Session(
                session_id=metadata['session_id'],
                name=metadata['name'],
                messages=messages,
                created_at=metadata.get('created_at', datetime.now().isoformat()),
                updated_at=metadata.get('updated_at', datetime.now().isoformat()),
                metadata=metadata.get('metadata', {})
            )
            
            # 设置为当前会话
            self.current_session = session
            
            logger.info(f"加载会话: {session_id} - {session.name}")
            
            return session
            
        except FileNotFoundError:
            raise
        except Exception as e:
            logger.error(f"加载会话失败: {session_id}, 错误: {e}", exc_info=True)
            raise ValueError(f"会话文件损坏: {session_id}")
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """
        列出所有会话
        
        Returns:
            List[Dict]: 会话列表，按更新时间倒序排列
        """
        sessions = []
        
        try:
            # 遍历存储目录
            for session_dir in self.storage_path.iterdir():
                if not session_dir.is_dir():
                    continue
                
                # 跳过已删除的会话
                deleted_flag = session_dir / ".deleted"
                if deleted_flag.exists():
                    logger.debug(f"跳过已删除的会话: {session_dir.name}")
                    continue
                
                try:
                    # 读取元数据
                    metadata_path = session_dir / "metadata.json"
                    if not metadata_path.exists():
                        continue
                    
                    with open(metadata_path, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    
                    # 添加预览信息
                    messages_path = session_dir / "messages.json"
                    preview = "暂无消息"
                    if messages_path.exists():
                        with open(messages_path, 'r', encoding='utf-8') as f:
                            messages_data = json.load(f)
                            if messages_data:
                                latest_msg = messages_data[-1]
                                content = latest_msg.get('content', '')
                                preview = content[:50] + "..." if len(content) > 50 else content
                    
                    metadata['preview'] = preview
                    sessions.append(metadata)
                    
                except Exception as e:
                    logger.warning(f"读取会话元数据失败: {session_dir.name}, 错误: {e}")
                    # 标记为损坏的会话
                    sessions.append({
                        'session_id': session_dir.name,
                        'name': '损坏的会话',
                        'created_at': '',
                        'updated_at': '',
                        'message_count': 0,
                        'preview': '会话文件损坏',
                        'corrupted': True
                    })
            
            # 按更新时间倒序排列
            sessions.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
            
            logger.debug(f"列出会话: 共 {len(sessions)} 个")
            
            return sessions
            
        except Exception as e:
            logger.error(f"列出会话失败, 错误: {e}", exc_info=True)
            return []
    
    def delete_session(self, session_id: str) -> None:
        """
        删除会话（软删除）
        
        不删除会话文件，只创建 .deleted 标志文件来标记删除
        
        Args:
            session_id: 会话 ID
            
        Raises:
            FileNotFoundError: 会话不存在
        """
        try:
            session_dir = self.storage_path / session_id
            
            if not session_dir.exists():
                raise FileNotFoundError(f"会话不存在: {session_id}")
            
            # 创建 .deleted 标志文件
            deleted_flag = session_dir / ".deleted"
            deleted_flag.touch()
            
            # 写入删除时间戳
            with open(deleted_flag, 'w', encoding='utf-8') as f:
                f.write(datetime.now().isoformat())
            
            # 如果删除的是当前会话，清空当前会话
            if self.current_session and self.current_session.session_id == session_id:
                self.current_session = None
            
            logger.info(f"删除会话（软删除）: {session_id}")
            
        except FileNotFoundError:
            raise
        except Exception as e:
            logger.error(f"删除会话失败: {session_id}, 错误: {e}", exc_info=True)
            raise
    
    def rename_session(self, session_id: str, new_name: str) -> None:
        """
        重命名会话
        
        Args:
            session_id: 会话 ID
            new_name: 新的会话名称
            
        Raises:
            FileNotFoundError: 会话不存在
        """
        try:
            session_dir = self.storage_path / session_id
            
            if not session_dir.exists():
                raise FileNotFoundError(f"会话不存在: {session_id}")
            
            # 读取元数据
            metadata_path = session_dir / "metadata.json"
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # 更新名称和时间戳
            metadata['name'] = new_name
            metadata['updated_at'] = datetime.now().isoformat()
            
            # 保存元数据
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            # 如果是当前会话，更新当前会话对象
            if self.current_session and self.current_session.session_id == session_id:
                self.current_session.name = new_name
                self.current_session.updated_at = metadata['updated_at']
            
            logger.info(f"重命名会话: {session_id} -> {new_name}")
            
        except FileNotFoundError:
            raise
        except Exception as e:
            logger.error(f"重命名会话失败: {session_id}, 错误: {e}", exc_info=True)
            raise
    
    def add_message(self, role: str, content: str) -> Optional[Message]:
        """
        向当前会话添加消息
        
        Args:
            role: 消息角色 ('user' or 'assistant')
            content: 消息内容
            
        Returns:
            Message: 创建的消息对象，如果没有当前会话返回 None
        """
        if self.current_session is None:
            logger.warning("没有当前会话，无法添加消息")
            return None
        
        message = self.current_session.add_message(role, content)
        
        # 自动保存
        if self.auto_save:
            self.save_session(self.current_session)
        
        logger.debug(f"添加消息到会话: {self.current_session.session_id}, 角色: {role}")
        
        return message
    
    def get_current_session(self) -> Optional[Session]:
        """
        获取当前会话
        
        Returns:
            Session: 当前会话对象，如果没有返回 None
        """
        return self.current_session
    
    def set_current_session(self, session: Session) -> None:
        """
        设置当前会话
        
        Args:
            session: 会话对象
        """
        self.current_session = session
        logger.info(f"设置当前会话: {session.session_id} - {session.name}")
    
    def rollback_to_message(self, sequence_number: int) -> bool:
        """
        回滚会话到指定消息
        
        将指定序号之后的所有消息标记为已回滚（通过元数据）
        
        Args:
            sequence_number: 消息序号
            
        Returns:
            bool: 是否成功回滚
        """
        if self.current_session is None:
            logger.warning("没有当前会话，无法回滚")
            return False
        
        # 检查序号是否有效
        if sequence_number < 0 or sequence_number >= len(self.current_session.messages):
            logger.warning(f"无效的消息序号: {sequence_number}")
            return False
        
        # 标记回滚点
        self.current_session.metadata['rollback_point'] = sequence_number
        self.current_session.metadata['rollback_timestamp'] = datetime.now().isoformat()
        
        # 保存会话
        if self.auto_save:
            self.save_session(self.current_session)
        
        logger.info(f"会话回滚到消息序号: {sequence_number}")
        
        return True
    
    def clear_rollback(self) -> bool:
        """
        清除会话的回滚标记
        
        Returns:
            bool: 是否成功清除
        """
        if self.current_session is None:
            logger.warning("没有当前会话，无法清除回滚")
            return False
        
        # 移除回滚标记
        if 'rollback_point' in self.current_session.metadata:
            del self.current_session.metadata['rollback_point']
        if 'rollback_timestamp' in self.current_session.metadata:
            del self.current_session.metadata['rollback_timestamp']
        
        # 保存会话
        if self.auto_save:
            self.save_session(self.current_session)
        
        logger.info("清除会话回滚标记")
        
        return True
    
    def get_rollback_point(self) -> Optional[int]:
        """
        获取当前会话的回滚点
        
        Returns:
            Optional[int]: 回滚点序号，如果没有回滚返回 None
        """
        if self.current_session is None:
            return None
        
        return self.current_session.metadata.get('rollback_point')
