"""
Advanced Analytics Manager for StarLabs Twitter Bot v3.0
Comprehensive analytics, reporting, and performance monitoring
"""

import json
import os
import asyncio
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import csv
from loguru import logger
import threading


class MetricType(Enum):
    SUCCESS_RATE = "success_rate"
    RESPONSE_TIME = "response_time"
    ERROR_RATE = "error_rate"
    THROUGHPUT = "throughput"
    ACCOUNT_HEALTH = "account_health"


class ReportType(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


@dataclass
class PerformanceMetric:
    timestamp: datetime
    metric_type: MetricType
    value: float
    account_id: str = ""
    task_type: str = ""
    additional_data: Dict = None
    
    def __post_init__(self):
        if self.additional_data is None:
            self.additional_data = {}
        if not isinstance(self.metric_type, MetricType):
            self.metric_type = MetricType(self.metric_type) if isinstance(self.metric_type, str) else MetricType.SUCCESS_RATE


@dataclass
class TaskExecution:
    task_id: str
    account_id: str
    task_type: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "running"  # running, success, failed, timeout
    error_message: str = ""
    response_time: float = 0.0
    retry_count: int = 0
    additional_data: Dict = None
    
    def __post_init__(self):
        if self.additional_data is None:
            self.additional_data = {}
    
    def complete(self, status: str, error_message: str = ""):
        """Mark task as completed"""
        self.end_time = datetime.now()
        self.status = status
        self.error_message = error_message
        if self.start_time:
            self.response_time = (self.end_time - self.start_time).total_seconds()


@dataclass
class AccountPerformance:
    account_id: str
    total_tasks: int = 0
    successful_tasks: int = 0
    failed_tasks: int = 0
    average_response_time: float = 0.0
    success_rate: float = 0.0
    last_activity: Optional[datetime] = None
    error_patterns: Dict[str, int] = None
    daily_stats: Dict[str, Dict] = None
    
    def __post_init__(self):
        if self.error_patterns is None:
            self.error_patterns = {}
        if self.daily_stats is None:
            self.daily_stats = {}
    
    def update_stats(self):
        """Update calculated statistics"""
        if self.total_tasks > 0:
            self.success_rate = (self.successful_tasks / self.total_tasks) * 100


class AdvancedAnalyticsManager:
    def __init__(self, data_dir: str = "data/analytics"):
        self.data_dir = data_dir
        self.metrics: List[PerformanceMetric] = []
        self.task_executions: List[TaskExecution] = []
        self.account_performances: Dict[str, AccountPerformance] = {}
        self._lock = threading.Lock()
        self._async_lock = asyncio.Lock()
        
        self.ensure_data_directory()
        self.load_analytics_data()
    
    def ensure_data_directory(self):
        """Ensure analytics directory exists"""
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(os.path.join(self.data_dir, "reports"), exist_ok=True)
        os.makedirs(os.path.join(self.data_dir, "exports"), exist_ok=True)
    
    def _serialize_metric(self, metric: PerformanceMetric) -> dict:
        """Serialize performance metric"""
        data = asdict(metric)
        data['timestamp'] = metric.timestamp.isoformat()
        data['metric_type'] = metric.metric_type.value
        return data
    
    def _deserialize_metric(self, data: dict) -> PerformanceMetric:
        """Deserialize performance metric"""
        if 'timestamp' in data:
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        if 'metric_type' in data:
            data['metric_type'] = MetricType(data['metric_type'])
        return PerformanceMetric(**data)
    
    def _serialize_task_execution(self, task: TaskExecution) -> dict:
        """Serialize task execution"""
        data = asdict(task)
        data['start_time'] = task.start_time.isoformat()
        if task.end_time:
            data['end_time'] = task.end_time.isoformat()
        return data
    
    def _deserialize_task_execution(self, data: dict) -> TaskExecution:
        """Deserialize task execution"""
        if 'start_time' in data:
            data['start_time'] = datetime.fromisoformat(data['start_time'])
        if 'end_time' in data and data['end_time']:
            data['end_time'] = datetime.fromisoformat(data['end_time'])
        return TaskExecution(**data)
    
    def record_metric(self, metric_type: MetricType, value: float, 
                     account_id: str = "", task_type: str = "", **kwargs):
        """Record a performance metric"""
        with self._lock:
            metric = PerformanceMetric(
                timestamp=datetime.now(),
                metric_type=metric_type,
                value=value,
                account_id=account_id,
                task_type=task_type,
                additional_data=kwargs
            )
            self.metrics.append(metric)
            
            # Keep only last 10000 metrics to prevent memory issues
            if len(self.metrics) > 10000:
                self.metrics = self.metrics[-8000:]  # Keep last 8000
    
    def start_task_tracking(self, account_id: str, task_type: str, **kwargs) -> str:
        """Start tracking a task execution"""
        task_id = f"{account_id}_{task_type}_{datetime.now().timestamp()}"
        
        task_execution = TaskExecution(
            task_id=task_id,
            account_id=account_id,
            task_type=task_type,
            start_time=datetime.now(),
            additional_data=kwargs
        )
        
        with self._lock:
            self.task_executions.append(task_execution)
        
        return task_id
    
    def complete_task_tracking(self, task_id: str, status: str, error_message: str = ""):
        """Complete task tracking"""
        with self._lock:
            for task in self.task_executions:
                if task.task_id == task_id:
                    task.complete(status, error_message)
                    
                    # Update account performance
                    self._update_account_performance(task)
                    
                    # Record metrics
                    self.record_metric(
                        MetricType.RESPONSE_TIME,
                        task.response_time,
                        task.account_id,
                        task.task_type
                    )
                    
                    if status == "success":
                        self.record_metric(MetricType.SUCCESS_RATE, 100, task.account_id, task.task_type)
                    else:
                        self.record_metric(MetricType.SUCCESS_RATE, 0, task.account_id, task.task_type)
                        self.record_metric(MetricType.ERROR_RATE, 1, task.account_id, task.task_type)
                    
                    break
    
    def _update_account_performance(self, task: TaskExecution):
        """Update account performance statistics"""
        account_id = task.account_id
        
        if account_id not in self.account_performances:
            self.account_performances[account_id] = AccountPerformance(account_id=account_id)
        
        perf = self.account_performances[account_id]
        perf.total_tasks += 1
        perf.last_activity = task.end_time or datetime.now()
        
        if task.status == "success":
            perf.successful_tasks += 1
        else:
            perf.failed_tasks += 1
            if task.error_message:
                perf.error_patterns[task.error_message] = perf.error_patterns.get(task.error_message, 0) + 1
        
        # Update average response time
        total_time = perf.average_response_time * (perf.total_tasks - 1) + task.response_time
        perf.average_response_time = total_time / perf.total_tasks
        
        # Update daily stats
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in perf.daily_stats:
            perf.daily_stats[today] = {"tasks": 0, "successes": 0, "failures": 0}
        
        perf.daily_stats[today]["tasks"] += 1
        if task.status == "success":
            perf.daily_stats[today]["successes"] += 1
        else:
            perf.daily_stats[today]["failures"] += 1
        
        perf.update_stats()
    
    def get_performance_summary(self, time_range: timedelta = None) -> Dict:
        """Get comprehensive performance summary"""
        if time_range is None:
            time_range = timedelta(days=7)  # Last 7 days by default
        
        cutoff_time = datetime.now() - time_range
        
        # Filter recent metrics
        recent_metrics = [m for m in self.metrics if m.timestamp >= cutoff_time]
        recent_tasks = [t for t in self.task_executions if t.start_time >= cutoff_time]
        
        summary = {
            "time_range": f"Last {time_range.days} days",
            "total_tasks": len(recent_tasks),
            "successful_tasks": len([t for t in recent_tasks if t.status == "success"]),
            "failed_tasks": len([t for t in recent_tasks if t.status == "failed"]),
            "average_response_time": 0,
            "success_rate": 0,
            "error_rate": 0,
            "throughput": 0,
            "top_errors": {},
            "task_breakdown": {},
            "account_breakdown": {},
            "hourly_distribution": {},
            "performance_trends": {}
        }
        
        if recent_tasks:
            # Calculate basic metrics
            successful_tasks = [t for t in recent_tasks if t.status == "success"]
            failed_tasks = [t for t in recent_tasks if t.status == "failed"]
            
            summary["success_rate"] = (len(successful_tasks) / len(recent_tasks)) * 100
            summary["error_rate"] = (len(failed_tasks) / len(recent_tasks)) * 100
            
            # Average response time
            completed_tasks = [t for t in recent_tasks if t.end_time]
            if completed_tasks:
                summary["average_response_time"] = sum(t.response_time for t in completed_tasks) / len(completed_tasks)
            
            # Throughput (tasks per hour)
            hours = max(1, time_range.total_seconds() / 3600)
            summary["throughput"] = len(recent_tasks) / hours
            
            # Task breakdown
            task_types = {}
            for task in recent_tasks:
                task_type = task.task_type
                if task_type not in task_types:
                    task_types[task_type] = {"total": 0, "success": 0, "failed": 0}
                
                task_types[task_type]["total"] += 1
                if task.status == "success":
                    task_types[task_type]["success"] += 1
                elif task.status == "failed":
                    task_types[task_type]["failed"] += 1
            
            summary["task_breakdown"] = task_types
            
            # Account breakdown
            account_stats = {}
            for task in recent_tasks:
                account_id = task.account_id
                if account_id not in account_stats:
                    account_stats[account_id] = {"total": 0, "success": 0, "failed": 0}
                
                account_stats[account_id]["total"] += 1
                if task.status == "success":
                    account_stats[account_id]["success"] += 1
                elif task.status == "failed":
                    account_stats[account_id]["failed"] += 1
            
            summary["account_breakdown"] = account_stats
            
            # Top errors
            error_counts = {}
            for task in failed_tasks:
                if task.error_message:
                    error_counts[task.error_message] = error_counts.get(task.error_message, 0) + 1
            
            summary["top_errors"] = dict(sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:10])
            
            # Hourly distribution
            hourly_stats = {}
            for task in recent_tasks:
                hour = task.start_time.hour
                if hour not in hourly_stats:
                    hourly_stats[hour] = 0
                hourly_stats[hour] += 1
            
            summary["hourly_distribution"] = hourly_stats
        
        return summary
    
    def generate_report(self, report_type: ReportType, start_date: datetime = None, 
                       end_date: datetime = None) -> Dict:
        """Generate comprehensive report"""
        if not start_date:
            if report_type == ReportType.DAILY:
                start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            elif report_type == ReportType.WEEKLY:
                start_date = datetime.now() - timedelta(days=7)
            elif report_type == ReportType.MONTHLY:
                start_date = datetime.now() - timedelta(days=30)
        
        if not end_date:
            end_date = datetime.now()
        
        # Filter data by date range
        filtered_tasks = [
            t for t in self.task_executions 
            if start_date <= t.start_time <= end_date
        ]
        
        filtered_metrics = [
            m for m in self.metrics 
            if start_date <= m.timestamp <= end_date
        ]
        
        report = {
            "report_type": report_type.value,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "generated_at": datetime.now().isoformat(),
            "summary": self._generate_summary_stats(filtered_tasks),
            "detailed_metrics": self._generate_detailed_metrics(filtered_metrics),
            "account_analysis": self._generate_account_analysis(filtered_tasks),
            "task_analysis": self._generate_task_analysis(filtered_tasks),
            "error_analysis": self._generate_error_analysis(filtered_tasks),
            "performance_trends": self._generate_performance_trends(filtered_metrics),
            "recommendations": self._generate_recommendations(filtered_tasks, filtered_metrics)
        }
        
        return report
    
    def _generate_summary_stats(self, tasks: List[TaskExecution]) -> Dict:
        """Generate summary statistics"""
        if not tasks:
            return {}
        
        successful = [t for t in tasks if t.status == "success"]
        failed = [t for t in tasks if t.status == "failed"]
        completed = [t for t in tasks if t.end_time]
        
        return {
            "total_tasks": len(tasks),
            "successful_tasks": len(successful),
            "failed_tasks": len(failed),
            "success_rate": (len(successful) / len(tasks)) * 100 if tasks else 0,
            "average_response_time": sum(t.response_time for t in completed) / len(completed) if completed else 0,
            "total_accounts": len(set(t.account_id for t in tasks)),
            "unique_task_types": len(set(t.task_type for t in tasks))
        }
    
    def _generate_detailed_metrics(self, metrics: List[PerformanceMetric]) -> Dict:
        """Generate detailed metrics analysis"""
        if not metrics:
            return {}
        
        metrics_by_type = {}
        for metric in metrics:
            metric_type = metric.metric_type.value
            if metric_type not in metrics_by_type:
                metrics_by_type[metric_type] = []
            metrics_by_type[metric_type].append(metric.value)
        
        detailed = {}
        for metric_type, values in metrics_by_type.items():
            detailed[metric_type] = {
                "count": len(values),
                "average": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
                "median": sorted(values)[len(values) // 2] if values else 0
            }
        
        return detailed
    
    def _generate_account_analysis(self, tasks: List[TaskExecution]) -> Dict:
        """Generate account-specific analysis"""
        account_stats = {}
        
        for task in tasks:
            account_id = task.account_id
            if account_id not in account_stats:
                account_stats[account_id] = {
                    "total_tasks": 0,
                    "successful_tasks": 0,
                    "failed_tasks": 0,
                    "average_response_time": 0,
                    "task_types": set()
                }
            
            stats = account_stats[account_id]
            stats["total_tasks"] += 1
            stats["task_types"].add(task.task_type)
            
            if task.status == "success":
                stats["successful_tasks"] += 1
            elif task.status == "failed":
                stats["failed_tasks"] += 1
            
            if task.response_time > 0:
                current_avg = stats["average_response_time"]
                total_tasks = stats["total_tasks"]
                stats["average_response_time"] = (current_avg * (total_tasks - 1) + task.response_time) / total_tasks
        
        # Convert sets to lists for JSON serialization
        for account_id, stats in account_stats.items():
            stats["task_types"] = list(stats["task_types"])
            stats["success_rate"] = (stats["successful_tasks"] / stats["total_tasks"]) * 100 if stats["total_tasks"] > 0 else 0
        
        return account_stats
    
    def _generate_task_analysis(self, tasks: List[TaskExecution]) -> Dict:
        """Generate task-specific analysis"""
        task_stats = {}
        
        for task in tasks:
            task_type = task.task_type
            if task_type not in task_stats:
                task_stats[task_type] = {
                    "total_executions": 0,
                    "successful_executions": 0,
                    "failed_executions": 0,
                    "average_response_time": 0,
                    "accounts_used": set()
                }
            
            stats = task_stats[task_type]
            stats["total_executions"] += 1
            stats["accounts_used"].add(task.account_id)
            
            if task.status == "success":
                stats["successful_executions"] += 1
            elif task.status == "failed":
                stats["failed_executions"] += 1
            
            if task.response_time > 0:
                current_avg = stats["average_response_time"]
                total_executions = stats["total_executions"]
                stats["average_response_time"] = (current_avg * (total_executions - 1) + task.response_time) / total_executions
        
        # Convert sets to lists and add success rates
        for task_type, stats in task_stats.items():
            stats["accounts_used"] = len(stats["accounts_used"])
            stats["success_rate"] = (stats["successful_executions"] / stats["total_executions"]) * 100 if stats["total_executions"] > 0 else 0
        
        return task_stats
    
    def _generate_error_analysis(self, tasks: List[TaskExecution]) -> Dict:
        """Generate error analysis"""
        failed_tasks = [t for t in tasks if t.status == "failed"]
        
        error_patterns = {}
        error_by_account = {}
        error_by_task_type = {}
        
        for task in failed_tasks:
            error_msg = task.error_message or "Unknown error"
            
            # Error patterns
            error_patterns[error_msg] = error_patterns.get(error_msg, 0) + 1
            
            # Errors by account
            if task.account_id not in error_by_account:
                error_by_account[task.account_id] = {}
            error_by_account[task.account_id][error_msg] = error_by_account[task.account_id].get(error_msg, 0) + 1
            
            # Errors by task type
            if task.task_type not in error_by_task_type:
                error_by_task_type[task.task_type] = {}
            error_by_task_type[task.task_type][error_msg] = error_by_task_type[task.task_type].get(error_msg, 0) + 1
        
        return {
            "total_errors": len(failed_tasks),
            "error_patterns": dict(sorted(error_patterns.items(), key=lambda x: x[1], reverse=True)),
            "errors_by_account": error_by_account,
            "errors_by_task_type": error_by_task_type
        }
    
    def _generate_performance_trends(self, metrics: List[PerformanceMetric]) -> Dict:
        """Generate performance trends"""
        if not metrics:
            return {}
        
        # Group metrics by day
        daily_metrics = {}
        for metric in metrics:
            day = metric.timestamp.strftime("%Y-%m-%d")
            if day not in daily_metrics:
                daily_metrics[day] = {metric_type.value: [] for metric_type in MetricType}
            
            daily_metrics[day][metric.metric_type.value].append(metric.value)
        
        # Calculate daily averages
        trends = {}
        for day, day_metrics in daily_metrics.items():
            trends[day] = {}
            for metric_type, values in day_metrics.items():
                if values:
                    trends[day][metric_type] = sum(values) / len(values)
                else:
                    trends[day][metric_type] = 0
        
        return trends
    
    def _generate_recommendations(self, tasks: List[TaskExecution], metrics: List[PerformanceMetric]) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []
        
        if not tasks:
            return recommendations
        
        # Analyze success rates
        successful_tasks = len([t for t in tasks if t.status == "success"])
        total_tasks = len(tasks)
        success_rate = (successful_tasks / total_tasks) * 100 if total_tasks > 0 else 0
        
        if success_rate < 70:
            recommendations.append("⚠️ Low success rate detected. Consider reviewing account health and proxy quality.")
        
        # Analyze response times
        completed_tasks = [t for t in tasks if t.end_time and t.response_time > 0]
        if completed_tasks:
            avg_response_time = sum(t.response_time for t in completed_tasks) / len(completed_tasks)
            if avg_response_time > 10:  # 10 seconds
                recommendations.append("🐌 High response times detected. Consider optimizing network settings or reducing concurrent requests.")
        
        # Analyze error patterns
        failed_tasks = [t for t in tasks if t.status == "failed"]
        if failed_tasks:
            error_counts = {}
            for task in failed_tasks:
                error_counts[task.error_message] = error_counts.get(task.error_message, 0) + 1
            
            most_common_error = max(error_counts.items(), key=lambda x: x[1])
            if most_common_error[1] > len(failed_tasks) * 0.5:  # More than 50% of errors
                recommendations.append(f"🔍 Frequent error detected: '{most_common_error[0]}'. Focus on resolving this issue.")
        
        # Analyze account distribution
        account_task_counts = {}
        for task in tasks:
            account_task_counts[task.account_id] = account_task_counts.get(task.account_id, 0) + 1
        
        if account_task_counts:
            max_tasks = max(account_task_counts.values())
            min_tasks = min(account_task_counts.values())
            if max_tasks > min_tasks * 3:  # Uneven distribution
                recommendations.append("⚖️ Uneven task distribution across accounts. Consider implementing better load balancing.")
        
        if not recommendations:
            recommendations.append("✅ Performance looks good! Keep up the excellent work.")
        
        return recommendations
    
    def export_report(self, report: Dict, filename: str, format: str = "json") -> bool:
        """Export report to file"""
        try:
            filepath = os.path.join(self.data_dir, "reports", filename)
            
            if format.lower() == "json":
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(report, f, indent=2, ensure_ascii=False)
            
            elif format.lower() == "csv":
                # Export summary as CSV
                with open(filepath, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    
                    # Write summary section
                    writer.writerow(["Summary Statistics"])
                    for key, value in report.get("summary", {}).items():
                        writer.writerow([key, value])
                    
                    writer.writerow([])  # Empty row
                    
                    # Write account analysis
                    writer.writerow(["Account Analysis"])
                    writer.writerow(["Account ID", "Total Tasks", "Success Rate", "Avg Response Time"])
                    for account_id, stats in report.get("account_analysis", {}).items():
                        writer.writerow([
                            account_id,
                            stats.get("total_tasks", 0),
                            f"{stats.get('success_rate', 0):.2f}%",
                            f"{stats.get('average_response_time', 0):.2f}s"
                        ])
            
            logger.success(f"Report exported to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error exporting report: {e}")
            return False
    
    def save_analytics_data(self):
        """Save analytics data to files"""
        try:
            # Save metrics
            metrics_file = os.path.join(self.data_dir, "metrics.json")
            serialized_metrics = [self._serialize_metric(m) for m in self.metrics[-1000:]]  # Keep last 1000
            with open(metrics_file, 'w', encoding='utf-8') as f:
                json.dump(serialized_metrics, f, indent=2)
            
            # Save task executions
            tasks_file = os.path.join(self.data_dir, "task_executions.json")
            serialized_tasks = [self._serialize_task_execution(t) for t in self.task_executions[-1000:]]  # Keep last 1000
            with open(tasks_file, 'w', encoding='utf-8') as f:
                json.dump(serialized_tasks, f, indent=2)
            
            # Save account performances
            accounts_file = os.path.join(self.data_dir, "account_performances.json")
            serialized_accounts = {}
            for account_id, perf in self.account_performances.items():
                serialized_accounts[account_id] = asdict(perf)
                if perf.last_activity:
                    serialized_accounts[account_id]['last_activity'] = perf.last_activity.isoformat()
            
            with open(accounts_file, 'w', encoding='utf-8') as f:
                json.dump(serialized_accounts, f, indent=2)
            
            logger.success("Analytics data saved successfully")
        except Exception as e:
            logger.error(f"Error saving analytics data: {e}")
    
    def load_analytics_data(self):
        """Load analytics data from files"""
        try:
            # Load metrics
            metrics_file = os.path.join(self.data_dir, "metrics.json")
            if os.path.exists(metrics_file):
                with open(metrics_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.metrics = [self._deserialize_metric(m) for m in data]
            
            # Load task executions
            tasks_file = os.path.join(self.data_dir, "task_executions.json")
            if os.path.exists(tasks_file):
                with open(tasks_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.task_executions = [self._deserialize_task_execution(t) for t in data]
            
            # Load account performances
            accounts_file = os.path.join(self.data_dir, "account_performances.json")
            if os.path.exists(accounts_file):
                with open(accounts_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for account_id, perf_data in data.items():
                        if 'last_activity' in perf_data and perf_data['last_activity']:
                            perf_data['last_activity'] = datetime.fromisoformat(perf_data['last_activity'])
                        self.account_performances[account_id] = AccountPerformance(**perf_data)
            
            logger.success("Analytics data loaded successfully")
        except Exception as e:
            logger.error(f"Error loading analytics data: {e}")
    
    def interactive_analytics_dashboard(self):
        """Interactive analytics dashboard"""
        while True:
            print("\n📊 Analytics Dashboard")
            print("=" * 40)
            
            print("[1] Performance Summary")
            print("[2] Generate Report")
            print("[3] Account Analysis")
            print("[4] Task Analysis")
            print("[5] Error Analysis")
            print("[6] Export Data")
            print("[7] Real-time Monitoring")
            print("[8] Back to main menu")
            
            choice = input("\nYour choice: ").strip()
            
            if choice == "1":
                self._show_performance_summary()
            elif choice == "2":
                self._generate_report_interactive()
            elif choice == "3":
                self._show_account_analysis()
            elif choice == "4":
                self._show_task_analysis()
            elif choice == "5":
                self._show_error_analysis()
            elif choice == "6":
                self._export_data_interactive()
            elif choice == "7":
                self._real_time_monitoring()
            elif choice == "8":
                break
            else:
                print("❌ Invalid choice")
    
    def _show_performance_summary(self):
        """Show performance summary"""
        summary = self.get_performance_summary()
        
        print("\n📈 Performance Summary (Last 7 Days)")
        print("=" * 50)
        print(f"Total Tasks: {summary['total_tasks']}")
        print(f"Success Rate: {summary['success_rate']:.2f}%")
        print(f"Average Response Time: {summary['average_response_time']:.2f}s")
        print(f"Throughput: {summary['throughput']:.2f} tasks/hour")
        
        if summary['top_errors']:
            print("\n🔍 Top Errors:")
            for error, count in list(summary['top_errors'].items())[:5]:
                print(f"  • {error}: {count} occurrences")
        
        input("\nPress Enter to continue...")
    
    def _generate_report_interactive(self):
        """Interactive report generation"""
        print("\n📋 Generate Report")
        print("[1] Daily Report")
        print("[2] Weekly Report")
        print("[3] Monthly Report")
        print("[4] Custom Date Range")
        
        choice = input("Report type: ").strip()
        
        report_type_map = {
            "1": ReportType.DAILY,
            "2": ReportType.WEEKLY,
            "3": ReportType.MONTHLY,
            "4": ReportType.CUSTOM
        }
        
        report_type = report_type_map.get(choice, ReportType.DAILY)
        
        start_date = None
        end_date = None
        
        if report_type == ReportType.CUSTOM:
            start_str = input("Start date (YYYY-MM-DD): ").strip()
            end_str = input("End date (YYYY-MM-DD): ").strip()
            
            try:
                start_date = datetime.strptime(start_str, "%Y-%m-%d")
                end_date = datetime.strptime(end_str, "%Y-%m-%d")
            except ValueError:
                print("❌ Invalid date format")
                return
        
        print("🔄 Generating report...")
        report = self.generate_report(report_type, start_date, end_date)
        
        # Display summary
        summary = report.get("summary", {})
        print(f"\n📊 Report Summary:")
        print(f"Total Tasks: {summary.get('total_tasks', 0)}")
        print(f"Success Rate: {summary.get('success_rate', 0):.2f}%")
        print(f"Average Response Time: {summary.get('average_response_time', 0):.2f}s")
        
        # Ask to export
        export = input("\nExport report? (y/n): ").strip().lower()
        if export == 'y':
            filename = input("Filename: ").strip()
            if filename:
                if self.export_report(report, filename):
                    print("✅ Report exported successfully")
                else:
                    print("❌ Export failed")


# Global analytics manager instance
_analytics_manager = None


def get_analytics_manager() -> AdvancedAnalyticsManager:
    """Get analytics manager singleton"""
    global _analytics_manager
    if _analytics_manager is None:
        _analytics_manager = AdvancedAnalyticsManager()
    return _analytics_manager