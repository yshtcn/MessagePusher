"""
任务队列模块

负责管理和处理系统中的各种任务，包括消息发送、AI处理等。
"""

import logging
import threading
import queue
import time
import uuid
from typing import Dict, Any, Optional, List, Callable, Tuple
from enum import Enum, auto

# 日志记录器
logger = logging.getLogger(__name__)


class TaskPriority(Enum):
    """任务优先级"""
    HIGH = 0    # 高优先级
    NORMAL = 1  # 正常优先级
    LOW = 2     # 低优先级


class TaskStatus(Enum):
    """任务状态"""
    PENDING = auto()    # 等待处理
    PROCESSING = auto() # 处理中
    COMPLETED = auto()  # 已完成
    FAILED = auto()     # 失败
    RETRYING = auto()   # 重试中
    CANCELLED = auto()  # 已取消


class TaskType(Enum):
    """任务类型"""
    SEND_MESSAGE = auto()        # 发送消息任务
    AI_PROCESS = auto()          # AI处理任务
    URL_FETCH = auto()           # URL抓取任务
    SYSTEM_MAINTENANCE = auto()  # 系统维护任务
    CUSTOM = auto()              # 自定义任务


class Task:
    """
    任务类
    
    表示一个可执行的任务，包含任务类型、数据和回调函数。
    """
    
    def __init__(self, 
                 task_type: TaskType, 
                 data: Dict[str, Any], 
                 priority: TaskPriority = TaskPriority.NORMAL,
                 callback: Optional[Callable[[Dict[str, Any]], None]] = None,
                 retry_count: int = 0,
                 max_retries: int = 3):
        """
        初始化任务
        
        Args:
            task_type: 任务类型
            data: 任务数据
            priority: 任务优先级，默认为正常优先级
            callback: 任务完成后的回调函数，默认为None
            retry_count: 重试次数，默认为0
            max_retries: 最大重试次数，默认为3
        """
        self.id = str(uuid.uuid4())
        self.task_type = task_type
        self.data = data
        self.priority = priority
        self.callback = callback
        self.status = TaskStatus.PENDING
        self.created_at = time.time()
        self.started_at = None
        self.completed_at = None
        self.error = None
        self.result = None
        self.retry_count = retry_count
        self.max_retries = max_retries
    
    def __lt__(self, other):
        """比较运算符，用于优先级队列排序"""
        if self.priority.value != other.priority.value:
            return self.priority.value < other.priority.value
        return self.created_at < other.created_at


class TaskQueue:
    """
    任务队列
    
    管理系统中的各种任务，提供任务的添加、获取和处理功能。
    """
    
    def __init__(self, **config):
        """
        初始化任务队列
        
        Args:
            **config: 配置参数
                - max_workers: 最大工作线程数，默认为5
                - worker_idle_timeout: 工作线程空闲超时时间，默认为1.0秒
                - max_retries: 最大重试次数，默认为3
                - retry_delay: 重试延迟时间，默认为5.0秒
        """
        self._queue = queue.PriorityQueue()
        self._tasks = {}  # 使用字典存储任务，方便根据ID查询
        self._lock = threading.RLock()
        self._stop_event = threading.Event()
        self._workers = []
        self._worker_count = 0
        self._task_handlers = {}
        
        # 默认配置
        self._config = {
            "max_workers": 5,
            "worker_idle_timeout": 1.0,
            "max_retries": 3,
            "retry_delay": 5.0
        }
        
        # 更新配置
        self._config.update(config)
        
        logger.debug("TaskQueue初始化完成")
    
    def configure(self, config: Dict[str, Any]):
        """
        配置任务队列
        
        Args:
            config: 配置字典
        """
        if "task_queue_max_workers" in config:
            self._config["max_workers"] = int(config["task_queue_max_workers"])
        
        if "task_queue_worker_idle_timeout" in config:
            self._config["worker_idle_timeout"] = float(config["task_queue_worker_idle_timeout"])
        
        if "task_queue_max_retries" in config:
            self._config["max_retries"] = int(config["task_queue_max_retries"])
        
        if "task_queue_retry_delay" in config:
            self._config["retry_delay"] = float(config["task_queue_retry_delay"])
        
        logger.debug(f"TaskQueue配置更新: {self._config}")
    
    def initialize(self):
        """初始化任务队列"""
        logger.info("初始化任务队列...")
    
    def start(self):
        """启动任务队列"""
        logger.info("启动任务队列...")
        self._stop_event.clear()
        
        # 创建工作线程
        self._worker_count = self._config["max_workers"]
        for i in range(self._worker_count):
            worker = threading.Thread(
                target=self._worker_loop,
                name=f"TaskQueue-Worker-{i}",
                daemon=True
            )
            self._workers.append(worker)
            worker.start()
        
        logger.info(f"任务队列已启动，工作线程数: {self._worker_count}")
    
    def stop(self):
        """停止任务队列"""
        logger.info("停止任务队列...")
        self._stop_event.set()
        
        # 等待所有工作线程结束
        for worker in self._workers:
            if worker.is_alive():
                worker.join(timeout=2.0)
        
        self._workers = []
        logger.info("任务队列已停止")
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取任务队列状态
        
        Returns:
            Dict[str, Any]: 状态信息
        """
        with self._lock:
            pending_tasks = sum(1 for task in self._tasks.values() if task.status == TaskStatus.PENDING)
            processing_tasks = sum(1 for task in self._tasks.values() if task.status == TaskStatus.PROCESSING)
            completed_tasks = sum(1 for task in self._tasks.values() if task.status == TaskStatus.COMPLETED)
            failed_tasks = sum(1 for task in self._tasks.values() if task.status == TaskStatus.FAILED)
            
            return {
                "queue_size": self._queue.qsize(),
                "worker_count": self._worker_count,
                "active_workers": sum(1 for worker in self._workers if worker.is_alive()),
                "tasks": {
                    "total": len(self._tasks),
                    "pending": pending_tasks,
                    "processing": processing_tasks,
                    "completed": completed_tasks,
                    "failed": failed_tasks
                }
            }
    
    def register_task_handler(self, task_type: TaskType, handler: Callable[[Task], None]):
        """
        注册任务处理器
        
        Args:
            task_type: 任务类型
            handler: 处理函数
        """
        self._task_handlers[task_type] = handler
        logger.debug(f"注册任务处理器: {task_type.name}")
    
    def add_task(self, task: Task) -> str:
        """
        添加任务到队列
        
        Args:
            task: 任务对象
            
        Returns:
            str: 任务ID
        """
        with self._lock:
            self._tasks[task.id] = task
            self._queue.put(task)
            logger.debug(f"添加任务: {task.id}, 类型: {task.task_type.name}, 优先级: {task.priority.name}")
            return task.id
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """
        获取任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            Optional[Task]: 任务对象，如果不存在则返回None
        """
        with self._lock:
            return self._tasks.get(task_id)
    
    def cancel_task(self, task_id: str) -> bool:
        """
        取消任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 是否成功取消
        """
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return False
            
            if task.status == TaskStatus.PENDING:
                task.status = TaskStatus.CANCELLED
                logger.debug(f"取消任务: {task_id}")
                return True
            
            return False
    
    def retry_task(self, task_id: str) -> bool:
        """
        重试任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 是否成功重试
        """
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return False
            
            if task.status == TaskStatus.FAILED and task.retry_count < task.max_retries:
                task.status = TaskStatus.PENDING
                task.retry_count += 1
                task.error = None
                self._queue.put(task)
                logger.debug(f"重试任务: {task_id}, 重试次数: {task.retry_count}")
                return True
            
            return False
    
    def _worker_loop(self):
        """工作线程循环"""
        logger.debug(f"工作线程 {threading.current_thread().name} 启动")
        
        while not self._stop_event.is_set():
            try:
                # 从队列获取任务，设置超时以便检查停止事件
                try:
                    task = self._queue.get(timeout=self._config["worker_idle_timeout"])
                except queue.Empty:
                    continue
                
                # 检查任务状态
                if task.status != TaskStatus.PENDING:
                    self._queue.task_done()
                    continue
                
                # 处理任务
                self._process_task(task)
                
                # 标记任务完成
                self._queue.task_done()
            
            except Exception as e:
                logger.error(f"工作线程处理任务时出错: {str(e)}", exc_info=True)
        
        logger.debug(f"工作线程 {threading.current_thread().name} 停止")
    
    def _process_task(self, task: Task):
        """
        处理任务
        
        Args:
            task: 任务对象
        """
        # 更新任务状态
        with self._lock:
            task.status = TaskStatus.PROCESSING
            task.started_at = time.time()
        
        logger.debug(f"开始处理任务: {task.id}, 类型: {task.task_type.name}")
        
        try:
            # 获取任务处理器
            handler = self._task_handlers.get(task.task_type)
            if not handler:
                raise ValueError(f"未找到任务类型 {task.task_type.name} 的处理器")
            
            # 调用处理器
            result = handler(task)
            
            # 更新任务状态
            with self._lock:
                task.status = TaskStatus.COMPLETED
                task.completed_at = time.time()
                task.result = result
            
            logger.debug(f"任务处理完成: {task.id}")
            
            # 调用回调函数
            if task.callback:
                try:
                    task.callback(task.result)
                except Exception as e:
                    logger.error(f"任务回调函数执行出错: {str(e)}", exc_info=True)
        
        except Exception as e:
            # 更新任务状态
            with self._lock:
                task.status = TaskStatus.FAILED
                task.completed_at = time.time()
                task.error = str(e)
            
            logger.error(f"任务处理失败: {task.id}, 错误: {str(e)}", exc_info=True)
            
            # 自动重试
            if task.retry_count < task.max_retries:
                threading.Timer(self._config["retry_delay"], self.retry_task, args=[task.id]).start()
    
    def clean_completed_tasks(self, max_age: float = 3600.0):
        """
        清理已完成的任务
        
        Args:
            max_age: 最大存活时间，单位为秒，默认为1小时
        """
        with self._lock:
            current_time = time.time()
            to_remove = []
            
            for task_id, task in self._tasks.items():
                if task.status in (TaskStatus.COMPLETED, TaskStatus.CANCELLED):
                    if task.completed_at and (current_time - task.completed_at) > max_age:
                        to_remove.append(task_id)
            
            for task_id in to_remove:
                del self._tasks[task_id]
            
            logger.debug(f"清理已完成任务: {len(to_remove)} 个")
    
    def create_task(self, 
                    task_type: TaskType, 
                    data: Dict[str, Any], 
                    priority: TaskPriority = TaskPriority.NORMAL,
                    callback: Optional[Callable[[Dict[str, Any]], None]] = None) -> str:
        """
        创建并添加任务
        
        Args:
            task_type: 任务类型
            data: 任务数据
            priority: 任务优先级，默认为正常优先级
            callback: 任务完成后的回调函数，默认为None
            
        Returns:
            str: 任务ID
        """
        task = Task(
            task_type=task_type,
            data=data,
            priority=priority,
            callback=callback,
            max_retries=self._config["max_retries"]
        )
        return self.add_task(task) 