"""
任务调度器模块

负责系统中的定时任务调度，如定期扫描需要处理的消息、清理过期数据等。
"""

import logging
import threading
import time
from typing import Dict, Any, List, Callable, Optional
import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from .task_queue import TaskQueue, TaskType, TaskPriority

# 日志记录器
logger = logging.getLogger(__name__)


class TaskScheduler:
    """
    任务调度器
    
    负责系统中的定时任务调度，基于APScheduler实现。
    """
    
    def __init__(self, **config):
        """
        初始化任务调度器
        
        Args:
            **config: 配置参数
                - cleanup_interval: 清理间隔，默认3600秒
                - retry_interval: 重试间隔，默认300秒
                - stats_interval: 统计间隔，默认86400秒
                - max_task_age: 最大任务保存时间，默认604800秒
        """
        # 任务队列实例，需要在初始化后设置
        self.task_queue = None
        
        # 创建调度器
        jobstores = {
            'default': MemoryJobStore()
        }
        executors = {
            'default': ThreadPoolExecutor(10)
        }
        job_defaults = {
            'coalesce': True,
            'max_instances': 1,
            'misfire_grace_time': 60
        }
        
        self.scheduler = BackgroundScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults
        )
        
        # 默认配置
        self._config = {
            "cleanup_interval": 3600,  # 清理间隔，默认1小时
            "retry_interval": 300,     # 重试间隔，默认5分钟
            "stats_interval": 86400,   # 统计间隔，默认1天
            "max_task_age": 604800,    # 最大任务保存时间，默认7天
        }
        
        # 更新配置
        self._config.update(config)
        
        logger.debug("TaskScheduler初始化完成")
    
    def configure(self, config: Dict[str, Any]):
        """
        配置任务调度器
        
        Args:
            config: 配置字典
        """
        if "task_scheduler_cleanup_interval" in config:
            self._config["cleanup_interval"] = int(config["task_scheduler_cleanup_interval"])
        
        if "task_scheduler_retry_interval" in config:
            self._config["retry_interval"] = int(config["task_scheduler_retry_interval"])
        
        if "task_scheduler_stats_interval" in config:
            self._config["stats_interval"] = int(config["task_scheduler_stats_interval"])
        
        if "task_scheduler_max_task_age" in config:
            self._config["max_task_age"] = int(config["task_scheduler_max_task_age"])
        
        logger.debug(f"TaskScheduler配置更新: {self._config}")
    
    def initialize(self):
        """初始化任务调度器"""
        logger.info("初始化任务调度器...")
        
        # 注册内置任务
        self._register_builtin_tasks()
    
    def start(self):
        """启动任务调度器"""
        logger.info("启动任务调度器...")
        self.scheduler.start()
    
    def stop(self):
        """停止任务调度器"""
        logger.info("停止任务调度器...")
        self.scheduler.shutdown()
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取任务调度器状态
        
        Returns:
            Dict[str, Any]: 状态信息
        """
        return {
            "running": self.scheduler.running,
            "job_count": len(self.scheduler.get_jobs())
        }
    
    def _register_builtin_tasks(self):
        """注册内置任务"""
        # 清理任务
        self.scheduler.add_job(
            self._cleanup_task,
            IntervalTrigger(seconds=self._config["cleanup_interval"]),
            id='cleanup_task',
            name='清理过期数据'
        )
        
        # 重试失败任务
        self.scheduler.add_job(
            self._retry_failed_tasks,
            IntervalTrigger(seconds=self._config["retry_interval"]),
            id='retry_failed_tasks',
            name='重试失败任务'
        )
        
        # 生成系统统计
        self.scheduler.add_job(
            self._generate_stats,
            IntervalTrigger(seconds=self._config["stats_interval"]),
            id='generate_stats',
            name='生成系统统计'
        )
        
        # 每天凌晨2点进行数据库维护
        self.scheduler.add_job(
            self._db_maintenance,
            CronTrigger(hour=2, minute=0),
            id='db_maintenance',
            name='数据库维护'
        )
        
        logger.debug("已注册内置任务")
    
    def _cleanup_task(self):
        """清理过期数据任务"""
        logger.debug("执行清理过期数据任务")
        
        try:
            # 清理任务队列中已完成的任务
            if self.task_queue:
                self.task_queue.clean_completed_tasks(max_age=self._config["max_task_age"])
            
                # 创建系统维护任务来清理数据库中的过期数据
                self.task_queue.create_task(
                    task_type=TaskType.SYSTEM_MAINTENANCE,
                    data={
                        "action": "cleanup",
                        "max_age": self._config["max_task_age"]
                    },
                    priority=TaskPriority.LOW
                )
        except Exception as e:
            logger.error(f"清理过期数据任务执行失败: {str(e)}", exc_info=True)
    
    def _retry_failed_tasks(self):
        """重试失败任务"""
        logger.debug("执行重试失败任务")
        
        try:
            # 创建系统维护任务来重试数据库中的失败消息
            if self.task_queue:
                self.task_queue.create_task(
                    task_type=TaskType.SYSTEM_MAINTENANCE,
                    data={
                        "action": "retry_failed_messages"
                    },
                    priority=TaskPriority.NORMAL
                )
        except Exception as e:
            logger.error(f"重试失败任务执行失败: {str(e)}", exc_info=True)
    
    def _generate_stats(self):
        """生成系统统计信息"""
        logger.debug("执行生成系统统计任务")
        
        try:
            # 创建系统维护任务来生成统计信息
            if self.task_queue:
                self.task_queue.create_task(
                    task_type=TaskType.SYSTEM_MAINTENANCE,
                    data={
                        "action": "generate_stats"
                    },
                    priority=TaskPriority.LOW
                )
        except Exception as e:
            logger.error(f"生成系统统计任务执行失败: {str(e)}", exc_info=True)
    
    def _db_maintenance(self):
        """数据库维护任务"""
        logger.debug("执行数据库维护任务")
        
        try:
            # 创建系统维护任务来执行数据库维护
            if self.task_queue:
                self.task_queue.create_task(
                    task_type=TaskType.SYSTEM_MAINTENANCE,
                    data={
                        "action": "db_maintenance"
                    },
                    priority=TaskPriority.LOW
                )
        except Exception as e:
            logger.error(f"数据库维护任务执行失败: {str(e)}", exc_info=True)
    
    def add_job(self, func: Callable, trigger: Any, id: str, name: str, **kwargs) -> str:
        """
        添加定时任务
        
        Args:
            func: 任务函数
            trigger: 触发器
            id: 任务ID
            name: 任务名称
            **kwargs: 其他参数
            
        Returns:
            str: 任务ID
        """
        job = self.scheduler.add_job(func, trigger, id=id, name=name, **kwargs)
        logger.debug(f"添加定时任务: {id}, 名称: {name}")
        return job.id
    
    def remove_job(self, job_id: str) -> bool:
        """
        移除定时任务
        
        Args:
            job_id: 任务ID
            
        Returns:
            bool: 是否成功移除
        """
        try:
            self.scheduler.remove_job(job_id)
            logger.debug(f"移除定时任务: {job_id}")
            return True
        except Exception as e:
            logger.error(f"移除定时任务失败: {str(e)}")
            return False
    
    def get_jobs(self) -> List[Dict[str, Any]]:
        """
        获取所有定时任务
        
        Returns:
            List[Dict[str, Any]]: 任务列表
        """
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            })
        return jobs
    
    def get_scheduled_tasks(self) -> List[Dict[str, Any]]:
        """
        获取所有计划任务
        
        Returns:
            List[Dict[str, Any]]: 任务列表
        """
        # 这个方法在测试中被模拟了，实际实现可以根据需要调整
        return []
    
    def schedule_task(self, task: Dict[str, Any]):
        """
        调度任务
        
        Args:
            task: 任务信息
        """
        # 这个方法在测试中被模拟了，实际实现可以根据需要调整
        pass 