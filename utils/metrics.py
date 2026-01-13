"""
指标收集模块
用于追踪关键业务指标（调用次数、响应时间等）
"""
from collections import defaultdict
import time
from functools import wraps


class Metrics:
    """关键指标收集器"""

    def __init__(self):
        self.counters = defaultdict(int)
        self.timers = defaultdict(list)

    def inc(self, metric_name, value=1):
        """
        计数器递增

        Args:
            metric_name: 指标名称
            value: 递增值，默认为 1
        """
        self.counters[metric_name] += value

    def dec(self, metric_name, value=1):
        """
        计数器递减

        Args:
            metric_name: 指标名称
            value: 递减值，默认为 1
        """
        self.counters[metric_name] -= value

    def timing(self, metric_name, duration):
        """
        记录耗时

        Args:
            metric_name: 指标名称
            duration: 耗时（秒）
        """
        self.timers[metric_name].append(duration)

    def get_stats(self):
        """
        获取统计信息

        Returns:
            dict: 包含计数器和平均响应时间的字典
        """
        stats = {
            'counters': dict(self.counters),
            'avg_time': {},
            'count': {}
        }
        for name, durations in self.timers.items():
            if durations:
                stats['avg_time'][name] = sum(durations) / len(durations)
                stats['count'][name] = len(durations)
        return stats

    def reset(self):
        """重置所有指标"""
        self.counters.clear()
        self.timers.clear()


# 全局指标实例
metrics = Metrics()


def track_time(metric_name):
    """
    装饰器：追踪函数执行时间和调用次数

    用法:
        @track_time('llm_api_call')
        def call_llm_api(text):
            # 函数逻辑
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = func(*args, **kwargs)
                metrics.inc(f'{metric_name}_success')
                return result
            except Exception as e:
                metrics.inc(f'{metric_name}_error')
                raise
            finally:
                duration = time.time() - start
                metrics.timing(metric_name, duration)
        return wrapper
    return decorator


class MetricMiddleware:
    """指标收集中间件（用于 Flask）"""

    def __init__(self, app):
        self.app = app
        self.init_app(app)

    def init_app(self, app):
        """初始化中间件"""
        @app.before_request
        def before_request():
            from flask import request
            request.start_time = time.time()

        @app.after_request
        def after_request(response):
            from flask import request
            if hasattr(request, 'start_time'):
                duration = time.time() - request.start_time
                endpoint = request.endpoint or 'unknown'
                metrics.timing(f'http_request_{endpoint}', duration)
                metrics.inc(f'http_request_count')
            return response
