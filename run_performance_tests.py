"""Script to run performance tests and generate reports for the multi-agent system."""

import os
import sys
import time
import json
import asyncio
import pytest
import psutil
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class PerformanceTest:
    """Class to manage performance testing."""
    
    def __init__(self):
        """Initialize performance test manager."""
        self.results_dir = Path("performance-reports")
        self.results_dir.mkdir(exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results: Dict[str, List[Dict[str, Any]]] = {}
        self.system_metrics: Dict[str, List[float]] = {
            "cpu_percent": [],
            "memory_percent": [],
            "io_counters": []
        }

    async def monitor_system_resources(self, interval: float = 1.0):
        """Monitor system resources during test execution."""
        while True:
            self.system_metrics["cpu_percent"].append(psutil.cpu_percent())
            self.system_metrics["memory_percent"].append(psutil.virtual_memory().percent)
            io = psutil.disk_io_counters()
            self.system_metrics["io_counters"].append(io.read_bytes + io.write_bytes)
            await asyncio.sleep(interval)

    def run_performance_tests(self):
        """Run performance tests and collect metrics."""
        print("Running performance tests...")
        
        # Run pytest with performance markers
        pytest_args = [
            "-v",
            "-m", "performance",
            "--benchmark-only",
            "--benchmark-group-by=func",
            "--benchmark-sort=mean",
            f"--benchmark-json={self.results_dir}/benchmark_{self.timestamp}.json"
        ]
        
        # Start resource monitoring
        monitor_task = asyncio.create_task(self.monitor_system_resources())
        
        try:
            # Run tests
            result = pytest.main(pytest_args)
            
            # Stop monitoring
            monitor_task.cancel()
            
            return result
            
        except Exception as e:
            print(f"Error running performance tests: {e}")
            monitor_task.cancel()
            return 1

    def generate_performance_report(self):
        """Generate performance test report."""
        print("Generating performance report...")
        
        report_path = self.results_dir / f"report_{self.timestamp}"
        report_path.mkdir(exist_ok=True)
        
        # Load benchmark results
        benchmark_file = self.results_dir / f"benchmark_{self.timestamp}.json"
        if benchmark_file.exists():
            with open(benchmark_file) as f:
                benchmark_data = json.load(f)
        else:
            print("No benchmark data found")
            return
        
        # Generate plots
        self._generate_benchmark_plots(benchmark_data, report_path)
        self._generate_resource_plots(report_path)
        
        # Generate HTML report
        self._generate_html_report(benchmark_data, report_path)

    def _generate_benchmark_plots(self, benchmark_data: dict, report_path: Path):
        """Generate plots from benchmark data."""
        # Mean execution time plot
        plt.figure(figsize=(12, 6))
        tests = [b["name"] for b in benchmark_data["benchmarks"]]
        times = [b["stats"]["mean"] for b in benchmark_data["benchmarks"]]
        plt.bar(tests, times)
        plt.title("Mean Execution Time by Test")
        plt.xlabel("Test Name")
        plt.ylabel("Time (seconds)")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(report_path / "mean_execution_time.png")
        plt.close()
        
        # Standard deviation plot
        plt.figure(figsize=(12, 6))
        stdevs = [b["stats"]["stddev"] for b in benchmark_data["benchmarks"]]
        plt.bar(tests, stdevs)
        plt.title("Execution Time Standard Deviation by Test")
        plt.xlabel("Test Name")
        plt.ylabel("Standard Deviation (seconds)")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(report_path / "execution_stddev.png")
        plt.close()

    def _generate_resource_plots(self, report_path: Path):
        """Generate plots from system resource metrics."""
        # CPU usage plot
        plt.figure(figsize=(12, 6))
        plt.plot(self.system_metrics["cpu_percent"])
        plt.title("CPU Usage During Tests")
        plt.xlabel("Time (seconds)")
        plt.ylabel("CPU Usage (%)")
        plt.tight_layout()
        plt.savefig(report_path / "cpu_usage.png")
        plt.close()
        
        # Memory usage plot
        plt.figure(figsize=(12, 6))
        plt.plot(self.system_metrics["memory_percent"])
        plt.title("Memory Usage During Tests")
        plt.xlabel("Time (seconds)")
        plt.ylabel("Memory Usage (%)")
        plt.tight_layout()
        plt.savefig(report_path / "memory_usage.png")
        plt.close()
        
        # I/O operations plot
        plt.figure(figsize=(12, 6))
        plt.plot(self.system_metrics["io_counters"])
        plt.title("I/O Operations During Tests")
        plt.xlabel("Time (seconds)")
        plt.ylabel("Bytes")
        plt.tight_layout()
        plt.savefig(report_path / "io_operations.png")
        plt.close()

    def _generate_html_report(self, benchmark_data: dict, report_path: Path):
        """Generate HTML report with all results."""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Performance Test Report - {self.timestamp}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1, h2 {{ color: #333; }}
                .section {{ margin: 20px 0; }}
                .plot {{ margin: 20px 0; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f5f5f5; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
            </style>
        </head>
        <body>
            <h1>Performance Test Report</h1>
            <p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            
            <div class="section">
                <h2>Benchmark Results</h2>
                <table>
                    <tr>
                        <th>Test Name</th>
                        <th>Mean Time (s)</th>
                        <th>Min Time (s)</th>
                        <th>Max Time (s)</th>
                        <th>StdDev</th>
                    </tr>
        """
        
        for benchmark in benchmark_data["benchmarks"]:
            html_content += f"""
                    <tr>
                        <td>{benchmark["name"]}</td>
                        <td>{benchmark["stats"]["mean"]:.6f}</td>
                        <td>{benchmark["stats"]["min"]:.6f}</td>
                        <td>{benchmark["stats"]["max"]:.6f}</td>
                        <td>{benchmark["stats"]["stddev"]:.6f}</td>
                    </tr>
            """
        
        html_content += """
                </table>
            </div>
            
            <div class="section">
                <h2>Performance Plots</h2>
                <div class="plot">
                    <h3>Mean Execution Time</h3>
                    <img src="mean_execution_time.png" alt="Mean Execution Time">
                </div>
                <div class="plot">
                    <h3>Execution Time Standard Deviation</h3>
                    <img src="execution_stddev.png" alt="Execution Standard Deviation">
                </div>
                <div class="plot">
                    <h3>CPU Usage</h3>
                    <img src="cpu_usage.png" alt="CPU Usage">
                </div>
                <div class="plot">
                    <h3>Memory Usage</h3>
                    <img src="memory_usage.png" alt="Memory Usage">
                </div>
                <div class="plot">
                    <h3>I/O Operations</h3>
                    <img src="io_operations.png" alt="I/O Operations">
                </div>
            </div>
            
            <div class="section">
                <h2>System Information</h2>
                <table>
                    <tr>
                        <th>Metric</th>
                        <th>Value</th>
                    </tr>
                    <tr>
                        <td>Python Version</td>
                        <td>{sys.version}</td>
                    </tr>
                    <tr>
                        <td>CPU Count</td>
                        <td>{psutil.cpu_count()}</td>
                    </tr>
                    <tr>
                        <td>Total Memory</td>
                        <td>{psutil.virtual_memory().total / (1024 * 1024 * 1024):.2f} GB</td>
                    </tr>
                </table>
            </div>
        </body>
        </html>
        """
        
        with open(report_path / "report.html", "w") as f:
            f.write(html_content)

def main():
    """Main entry point for running performance tests."""
    try:
        # Create performance test manager
        perf_test = PerformanceTest()
        
        # Run tests
        result = perf_test.run_performance_tests()
        
        if result == 0:
            # Generate report
            perf_test.generate_performance_report()
            print("\nPerformance tests completed successfully!")
            print(f"Report generated in: {perf_test.results_dir}")
            return 0
        else:
            print("\nPerformance tests failed!")
            return 1
            
    except KeyboardInterrupt:
        print("\nPerformance tests interrupted by user")
        return 1
        
    except Exception as e:
        print(f"\nError during performance testing: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 