"""Performance monitoring and optimization utilities."""

import logging
import time
import psutil
import asyncio
from typing import Dict, Any, Optional
from contextlib import contextmanager
from datetime import datetime
from dataclasses import dataclass
import tracemalloc
from functools import wraps

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Container for performance metrics."""
    execution_time: float
    memory_used: int
    cpu_percent: float
    timestamp: str = datetime.utcnow().isoformat()

class PerformanceMonitor:
    """Monitors system and application performance."""
    
    def __init__(self):
        self.process = psutil.Process()
        self.metrics_history: Dict[str, list] = {}
        tracemalloc.start()
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics."""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_process_metrics(self) -> Dict[str, Any]:
        """Get current process metrics."""
        return {
            "cpu_percent": self.process.cpu_percent(),
            "memory_info": dict(self.process.memory_info()._asdict()),
            "num_threads": self.process.num_threads(),
            "num_fds": self.process.num_fds(),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def record_metrics(self, operation: str, metrics: PerformanceMetrics):
        """Record performance metrics for an operation."""
        if operation not in self.metrics_history:
            self.metrics_history[operation] = []
        
        self.metrics_history[operation].append({
            "execution_time": metrics.execution_time,
            "memory_used": metrics.memory_used,
            "cpu_percent": metrics.cpu_percent,
            "timestamp": metrics.timestamp
        })
        
        # Keep only last 1000 metrics per operation
        if len(self.metrics_history[operation]) > 1000:
            self.metrics_history[operation].pop(0)
    
    def get_metrics_summary(self, operation: str) -> Dict[str, Any]:
        """Get summary statistics for an operation."""
        if operation not in self.metrics_history:
            return {}
        
        metrics = self.metrics_history[operation]
        execution_times = [m["execution_time"] for m in metrics]
        memory_used = [m["memory_used"] for m in metrics]
        cpu_percent = [m["cpu_percent"] for m in metrics]
        
        return {
            "execution_time": {
                "avg": sum(execution_times) / len(execution_times),
                "min": min(execution_times),
                "max": max(execution_times)
            },
            "memory_used": {
                "avg": sum(memory_used) / len(memory_used),
                "min": min(memory_used),
                "max": max(memory_used)
            },
            "cpu_percent": {
                "avg": sum(cpu_percent) / len(cpu_percent),
                "min": min(cpu_percent),
                "max": max(cpu_percent)
            },
            "num_samples": len(metrics)
        }
    
    def get_memory_snapshot(self) -> Dict[str, Any]:
        """Get detailed memory usage snapshot."""
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')
        
        return {
            "top_memory_users": [
                {
                    "file": str(stat.traceback[0]),
                    "line": stat.traceback[0].lineno,
                    "size": stat.size,
                    "count": stat.count
                }
                for stat in top_stats[:10]  # Top 10 memory users
            ],
            "total_memory": sum(stat.size for stat in top_stats),
            "timestamp": datetime.utcnow().isoformat()
        }

# Global performance monitor instance
monitor = PerformanceMonitor()

@contextmanager
def timer(operation: Optional[str] = None):
    """Context manager for timing code execution."""
    start_time = time.time()
    start_memory = monitor.process.memory_info().rss
    start_cpu = monitor.process.cpu_percent()
    
    try:
        yield
    finally:
        end_time = time.time()
        end_memory = monitor.process.memory_info().rss
        end_cpu = monitor.process.cpu_percent()
        
        metrics = PerformanceMetrics(
            execution_time=end_time - start_time,
            memory_used=end_memory - start_memory,
            cpu_percent=end_cpu - start_cpu
        )
        
        if operation:
            monitor.record_metrics(operation, metrics)

@contextmanager
def memory_usage():
    """Context manager for tracking memory usage."""
    tracemalloc.start()
    
    try:
        yield
    finally:
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')
        
        logger.debug("Memory usage:")
        for stat in top_stats[:3]:  # Log top 3 memory users
            logger.debug(f"{stat.size/1024:.1f} KB - {stat.traceback[0]}")
        
        tracemalloc.stop()

def track_performance(operation: str):
    """Decorator for tracking function performance."""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            with timer(operation):
                return await func(*args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            with timer(operation):
                return func(*args, **kwargs)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

async def monitor_system_health():
    """Background task for monitoring system health."""
    while True:
        try:
            # Get current metrics
            system_metrics = monitor.get_system_metrics()
            process_metrics = monitor.get_process_metrics()
            
            # Log warnings for high resource usage
            if system_metrics["cpu_percent"] > 80:
                logger.warning("High CPU usage detected")
            
            if system_metrics["memory_percent"] > 80:
                logger.warning("High memory usage detected")
            
            if system_metrics["disk_usage"] > 80:
                logger.warning("High disk usage detected")
            
        except Exception as e:
            logger.error(f"Error monitoring system health: {str(e)}")
        
        await asyncio.sleep(60)  # Check every minute 