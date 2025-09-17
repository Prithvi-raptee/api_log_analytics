import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import glob
from typing import Dict, List, Tuple, Optional
import json
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.dates import DateFormatter
import warnings

warnings.filterwarnings('ignore')

def analyze_api_logs(csv_files_pattern: str = "*.csv", output_format: str = "json", generate_charts: bool = False) -> Dict:
    """
    Analyze API logs from CSV files and provide comprehensive metrics.
    
    Args:
        csv_files_pattern: Pattern to match CSV files (e.g., "logs/*.csv", "api_logs_*.csv")
        output_format: Output format - "json", "dict", or "pretty"
        generate_charts: Whether to generate visualization charts after analysis
    
    Returns:
        Dictionary containing analysis results for different time periods
    """
    
    # Get all CSV files matching the pattern
    csv_files = glob.glob(csv_files_pattern)
    
    if not csv_files:
        print(f"No CSV files found matching pattern: {csv_files_pattern}")
        return {}
    
    # Read and combine all CSV files
    all_data = []
    for file in csv_files:
        try:
            df = pd.read_csv(file)
            df['source_file'] = file
            all_data.append(df)
            print(f"Loaded {len(df)} records from {file}")
        except Exception as e:
            print(f"Error reading {file}: {e}")
            continue
    
    if not all_data:
        print("No valid data found in CSV files")
        return {}
    
    # Combine all dataframes
    df = pd.concat(all_data, ignore_index=True)
    
    # Clean and prepare data
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['success'] = df['status'] == 'success'
    df['latency_ms'] = pd.to_numeric(df['latency_ms'], errors='coerce')
    
    # Remove rows with invalid data
    df = df.dropna(subset=['timestamp', 'latency_ms'])
    
    print(f"Total records processed: {len(df)}")
    
    # Define time periods
    now = datetime.now()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)
    
    time_periods = {
        'today': df[df['timestamp'] >= today],
        'this_week': df[df['timestamp'] >= week_start],
        'this_month': df[df['timestamp'] >= month_start],
        'last_7_days': df[df['timestamp'] >= (now - timedelta(days=7))],
        'last_30_days': df[df['timestamp'] >= (now - timedelta(days=30))],
        'all_time': df
    }
    
    def calculate_metrics(data: pd.DataFrame) -> Dict:
        """Calculate metrics for a given dataset"""
        if len(data) == 0:
            return {
                'total_requests': 0,
                'success_count': 0,
                'failure_count': 0,
                'success_rate': 0.0,
                'failure_rate': 0.0,
                'avg_response_time_ms': 0.0,
                'min_response_time_ms': 0.0,
                'max_response_time_ms': 0.0,
                'median_response_time_ms': 0.0,
                'p95_response_time_ms': 0.0,
                'p99_response_time_ms': 0.0,
                'avg_success_response_time_ms': 0.0,
                'min_success_response_time_ms': 0.0,
                'max_success_response_time_ms': 0.0,
                'avg_failure_response_time_ms': 0.0
            }
        
        success_data = data[data['success']]
        failure_data = data[~data['success']]
        
        metrics = {
            'total_requests': len(data),
            'success_count': len(success_data),
            'failure_count': len(failure_data),
            'success_rate': len(success_data) / len(data) * 100,
            'failure_rate': len(failure_data) / len(data) * 100,
            'avg_response_time_ms': data['latency_ms'].mean(),
            'min_response_time_ms': data['latency_ms'].min(),
            'max_response_time_ms': data['latency_ms'].max(),
            'median_response_time_ms': data['latency_ms'].median(),
            'p95_response_time_ms': data['latency_ms'].quantile(0.95),
            'p99_response_time_ms': data['latency_ms'].quantile(0.99)
        }
        
        # Success-specific metrics
        if len(success_data) > 0:
            metrics.update({
                'avg_success_response_time_ms': success_data['latency_ms'].mean(),
                'min_success_response_time_ms': success_data['latency_ms'].min(),
                'max_success_response_time_ms': success_data['latency_ms'].max()
            })
        else:
            metrics.update({
                'avg_success_response_time_ms': 0.0,
                'min_success_response_time_ms': 0.0,
                'max_success_response_time_ms': 0.0
            })
        
        # Failure-specific metrics
        if len(failure_data) > 0:
            metrics['avg_failure_response_time_ms'] = failure_data['latency_ms'].mean()
        else:
            metrics['avg_failure_response_time_ms'] = 0.0
        
        # Round numeric values for cleaner output
        for key, value in metrics.items():
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                metrics[key] = round(value, 2)
        
        return metrics
    
    # Calculate metrics for each time period
    results = {}
    for period_name, period_data in time_periods.items():
        results[period_name] = calculate_metrics(period_data)
    
    # Add summary information
    results['summary'] = {
        'analysis_date': now.strftime('%Y-%m-%d %H:%M:%S'),
        'files_analyzed': csv_files,
        'date_range': {
            'earliest': df['timestamp'].min().strftime('%Y-%m-%d %H:%M:%S'),
            'latest': df['timestamp'].max().strftime('%Y-%m-%d %H:%M:%S')
        },
        'unique_endpoints': df['api_call'].nunique(),
        'total_records_processed': len(df)
    }
    
    # Store dataframe for visualization
    results['_dataframe'] = df
    
    # Format output based on requested format
    if output_format == "pretty":
        print_pretty_results(results)
        if generate_charts:
            generate_visualizations(df, results)
        return results
    elif output_format == "json":
        # Remove dataframe before JSON output
        results_copy = {k: v for k, v in results.items() if k != '_dataframe'}
        print(json.dumps(results_copy, indent=2, default=str))
        if generate_charts:
            generate_visualizations(df, results)
        return results
    else:
        if generate_charts:
            generate_visualizations(df, results)
        return results

def print_pretty_results(results: Dict):
    """Print results in a clean, readable format"""
    
    print("\n" + "="*80)
    print("API LOG ANALYSIS RESULTS")
    print("="*80)
    
    # Print summary
    summary = results['summary']
    print(f"\nANALYSIS SUMMARY")
    print(f"   Analysis Date: {summary['analysis_date']}")
    print(f"   Files Analyzed: {len(summary['files_analyzed'])}")
    print(f"   Date Range: {summary['date_range']['earliest']} to {summary['date_range']['latest']}")
    print(f"   Unique Endpoints: {summary['unique_endpoints']}")
    print(f"   Total Records: {summary['total_records_processed']}")
    
    # Define the order of time periods for better readability
    period_order = ['today', 'this_week', 'this_month', 'last_7_days', 'last_30_days', 'all_time']
    period_labels = {
        'today': 'TODAY',
        'this_week': 'THIS WEEK', 
        'this_month': 'THIS MONTH',
        'last_7_days': 'LAST 7 DAYS',
        'last_30_days': 'LAST 30 DAYS',
        'all_time': 'ALL TIME'
    }
    
    for period in period_order:
        if period in results and period != 'summary':
            metrics = results[period]
            if metrics['total_requests'] == 0:
                continue
                
            print(f"\n{period_labels[period]}")
            print("-" * 50)
            
            # Request counts and rates
            print(f"   Total Requests: {metrics['total_requests']:,}")
            print(f"   Success: {metrics['success_count']:,} ({metrics['success_rate']:.1f}%)")
            print(f"   Failures: {metrics['failure_count']:,} ({metrics['failure_rate']:.1f}%)")
            
            # Response time metrics
            print(f"\n   RESPONSE TIME METRICS (ms)")
            print(f"   Average: {metrics['avg_response_time_ms']:,.0f}")
            print(f"   Median: {metrics['median_response_time_ms']:,.0f}")
            print(f"   Min: {metrics['min_response_time_ms']:,.0f}")
            print(f"   Max: {metrics['max_response_time_ms']:,.0f}")
            print(f"   95th percentile: {metrics['p95_response_time_ms']:,.0f}")
            print(f"   99th percentile: {metrics['p99_response_time_ms']:,.0f}")
            
            # Success-specific metrics
            if metrics['success_count'] > 0:
                print(f"\n   SUCCESS RESPONSE TIMES (ms)")
                print(f"   Average: {metrics['avg_success_response_time_ms']:,.0f}")
                print(f"   Min: {metrics['min_success_response_time_ms']:,.0f}")
                print(f"   Max: {metrics['max_success_response_time_ms']:,.0f}")
            
            # Failure-specific metrics
            if metrics['failure_count'] > 0:
                print(f"\n   FAILURE RESPONSE TIMES (ms)")
                print(f"   Average: {metrics['avg_failure_response_time_ms']:,.0f}")

def generate_visualizations(df: pd.DataFrame, results: Dict):
    """Generate visualization charts for the API log analysis"""
    
    # Set up the plotting style
    plt.style.use('default')
    sns.set_palette("husl")
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('API Log Analysis Dashboard', fontsize=16, fontweight='bold')
    
    # 1. Success Rate Over Time
    ax1 = axes[0, 0]
    df_hourly = df.set_index('timestamp').resample('H').agg({
        'success': ['count', 'sum']
    }).fillna(0)
    df_hourly.columns = ['total_requests', 'successful_requests']
    df_hourly['success_rate'] = (df_hourly['successful_requests'] / df_hourly['total_requests'] * 100).fillna(0)
    
    ax1.plot(df_hourly.index, df_hourly['success_rate'], marker='o', linewidth=2, markersize=4)
    ax1.set_title('Success Rate Over Time', fontweight='bold')
    ax1.set_ylabel('Success Rate (%)')
    ax1.set_ylim(0, 105)
    ax1.grid(True, alpha=0.3)
    ax1.xaxis.set_major_formatter(DateFormatter('%m/%d %H:%M'))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
    
    # 2. Response Time Distribution
    ax2 = axes[0, 1]
    success_data = df[df['success']]['latency_ms']
    failure_data = df[~df['success']]['latency_ms']
    
    bins = np.linspace(0, min(df['latency_ms'].quantile(0.95), 50000), 30)
    ax2.hist(success_data, bins=bins, alpha=0.7, label='Success', color='green')
    ax2.hist(failure_data, bins=bins, alpha=0.7, label='Failure', color='red')
    ax2.set_title('Response Time Distribution', fontweight='bold')
    ax2.set_xlabel('Response Time (ms)')
    ax2.set_ylabel('Frequency')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Response Time Over Time
    ax3 = axes[1, 0]
    df_resampled = df.set_index('timestamp').resample('H')['latency_ms'].mean().fillna(0)
    ax3.plot(df_resampled.index, df_resampled.values, marker='s', linewidth=2, markersize=4, color='orange')
    ax3.set_title('Average Response Time Over Time', fontweight='bold')
    ax3.set_ylabel('Response Time (ms)')
    ax3.grid(True, alpha=0.3)
    ax3.xaxis.set_major_formatter(DateFormatter('%m/%d %H:%M'))
    plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45)
    
    # 4. Success vs Failure Count by Time Period
    ax4 = axes[1, 1]
    periods = ['today', 'last_7_days', 'last_30_days', 'all_time']
    period_labels = ['Today', 'Last 7 Days', 'Last 30 Days', 'All Time']
    success_counts = [results[p]['success_count'] for p in periods]
    failure_counts = [results[p]['failure_count'] for p in periods]
    
    x = np.arange(len(period_labels))
    width = 0.35
    
    bars1 = ax4.bar(x - width/2, success_counts, width, label='Success', color='green', alpha=0.7)
    bars2 = ax4.bar(x + width/2, failure_counts, width, label='Failure', color='red', alpha=0.7)
    
    ax4.set_title('Request Counts by Time Period', fontweight='bold')
    ax4.set_xlabel('Time Period')
    ax4.set_ylabel('Number of Requests')
    ax4.set_xticks(x)
    ax4.set_xticklabels(period_labels)
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax4.annotate(f'{int(height)}',
                           xy=(bar.get_x() + bar.get_width() / 2, height),
                           xytext=(0, 3),
                           textcoords="offset points",
                           ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    
    # Save the plot
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'api_log_analysis_{timestamp}.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"\nVisualization saved as: {filename}")
    
    # Show the plot
    plt.show()

def prompt_for_charts():
    """Ask user if they want to generate charts"""
    response = input("\nWould you like to generate visualization charts? (y/N): ").strip().lower()
    return response in ['y', 'yes', '1', 'true']

# Example usage:
if __name__ == "__main__":
    # Example 1: Analyze all CSV files in current directory with pretty output
    results = analyze_api_logs("*.csv", "pretty")
    
    # Ask if user wants charts after showing results
    if prompt_for_charts():
        print("\nGenerating charts...")
        # Re-run analysis with chart generation
        results = analyze_api_logs("*.csv", "pretty", generate_charts=True)
    
    # Example 2: Direct chart generation
    # results = analyze_api_logs("api_logs_*.csv", "pretty", generate_charts=True)
    
    # Example 3: Programmatic usage
    # results = analyze_api_logs("logs/*.csv", "dict", generate_charts=False)