"""Performance monitoring utilities for the Library of Alexandria."""

import time
import psutil
import functools
from typing import Any, Callable, Dict, Optional, TypeVar, cast
from dataclasses import dataclass
from datetime import datetime
import threading
from contextlib import contextmanager
import logging

# Type variables for generic function decorators
F = TypeVar('F', bound=Callable[..., Any])

@dataclass
class PerformanceMetrics:
    """Container for performance metrics."""
    execution_time: float
    memory_used: float
    cpu_percent: float
    timestamp: datetime
    function_name: str
    success: bool
    error: Optional[str] = None

class PerformanceMonitor:
    """Singleton class for tracking system-wide performance metrics."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialize()
            return cls._instance
    
    def _initialize(self):
        """Initialize the performance monitor."""
        self.metrics: Dict[str, list[PerformanceMetrics]] = {}
        self.logger = logging.getLogger('performance_monitor')
        self.process = psutil.Process()
    
    def record_metric(self, metric: PerformanceMetrics):
        """Record a performance metric."""
        with self._lock:
            if metric.function_name not in self.metrics:
                self.metrics[metric.function_name] = []
            self.metrics[metric.function_name].append(metric)
    
    def get_metrics(self, function_name: Optional[str] = None) -> Dict[str, list[PerformanceMetrics]]:
        """Get recorded metrics, optionally filtered by function name."""
        with self._lock:
            if function_name:
                return {function_name: self.metrics.get(function_name, [])}
            return self.metrics.copy()
    
    def clear_metrics(self, function_name: Optional[str] = None):
        """Clear recorded metrics, optionally for a specific function."""
        with self._lock:
            if function_name:
                self.metrics.pop(function_name, None)
            else:
                self.metrics.clear()

def timer(func: F) -> F:
    """Decorator to measure function execution time."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        monitor = PerformanceMonitor()
        start_time = time.time()
        start_memory = monitor.process.memory_info().rss / 1024 / 1024  # MB
        
        try:
            result = func(*args, **kwargs)
            success = True
            error = None
        except Exception as e:
            success = False
            error = str(e)
            raise
        finally:
            end_time = time.time()
            end_memory = monitor.process.memory_info().rss / 1024 / 1024  # MB
            
            metric = PerformanceMetrics(
                execution_time=end_time - start_time,
                memory_used=end_memory - start_memory,
                cpu_percent=monitor.process.cpu_percent(),
                timestamp=datetime.now(),
                function_name=func.__name__,
                success=success,
                error=error
            )
            
            monitor.record_metric(metric)
        
        return result
    
    return cast(F, wrapper)

@contextmanager
def memory_usage():
    """Context manager to measure memory usage."""
    process = psutil.Process()
    start_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    try:
        yield
    finally:
        end_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_used = end_memory - start_memory
        logging.getLogger('performance_monitor').info(
            f'Memory usage: {memory_used:.2f} MB'
        )

def get_system_metrics() -> Dict[str, float]:
    """Get current system metrics."""
    return {
        'cpu_percent': psutil.cpu_percent(),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_usage_percent': psutil.disk_usage('/').percent,
        'swap_memory_percent': psutil.swap_memory().percent
    }

def profile_generator(generator_func: Callable):
    """Decorator to profile generator functions."""
    @functools.wraps(generator_func)
    def wrapper(*args, **kwargs):
        monitor = PerformanceMonitor()
        start_time = time.time()
        start_memory = monitor.process.memory_info().rss / 1024 / 1024
        
        try:
            for item in generator_func(*args, **kwargs):
                current_memory = monitor.process.memory_info().rss / 1024 / 1024
                current_time = time.time() - start_time
                
                metric = PerformanceMetrics(
                    execution_time=current_time,
                    memory_used=current_memory - start_memory,
                    cpu_percent=monitor.process.cpu_percent(),
                    timestamp=datetime.now(),
                    function_name=f'{generator_func.__name__}_generator',
                    success=True
                )
                
                monitor.record_metric(metric)
                yield item
                
        except Exception as e:
            metric = PerformanceMetrics(
                execution_time=time.time() - start_time,
                memory_used=monitor.process.memory_info().rss / 1024 / 1024 - start_memory,
                cpu_percent=monitor.process.cpu_percent(),
                timestamp=datetime.now(),
                function_name=f'{generator_func.__name__}_generator',
                success=False,
                error=str(e)
            )
            monitor.record_metric(metric)
            raise
            
    return wrapper 