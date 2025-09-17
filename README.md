# API Log Analyzer

A comprehensive Python tool for analyzing API performance logs from CSV files. Track success rates, response times, and performance metrics across different time periods with clean, organized output and optional data visualizations.

## Features

- **Multi-file Processing**: Analyze multiple CSV files at once using glob patterns
- **Time-based Analysis**: Get metrics for today, this week, this month, last 7/30 days, and all-time
- **Comprehensive Metrics**: Success rates, response times, percentiles, and failure analysis
- **Multiple Output Formats**: Pretty console output, JSON, or raw dictionary
- **Data Visualization**: Optional chart generation with detailed performance graphs
- **Robust Data Handling**: Automatic data cleaning and validation
- **Performance Insights**: Identify bottlenecks and track API health over time

## Requirements

```bash
pip install pandas numpy matplotlib seaborn
```

## Expected CSV Format

Your CSV files should contain the following columns:
- `timestamp`: Request timestamp (ISO format recommended)
- `api_call`: API endpoint URL
- `latency_ms`: Response time in milliseconds
- `status`: Request status (`success` or `failure`)

Example CSV structure:
```csv
timestamp,api_call,latency_ms,status
"2025-09-15T16:02:40.057164","https://api.example.com/endpoint",7575,success
"2025-09-15T16:03:10.784079","https://api.example.com/endpoint",4512,success
"2025-09-15T16:08:59.289937","https://api.example.com/endpoint",7986,failure
```

## Usage

### Basic Usage

```python
from api_log_analyzer import analyze_api_logs

# Analyze all CSV files in current directory with pretty output
results = analyze_api_logs("*.csv", "pretty")

# Generate charts automatically
results = analyze_api_logs("*.csv", "pretty", generate_charts=True)
```

### Advanced Usage

```python
# Analyze specific files with JSON output
results = analyze_api_logs("api_logs_*.csv", "json")

# Analyze files in a specific directory with charts
results = analyze_api_logs("logs/*.csv", "pretty", generate_charts=True)

# Process files matching a specific pattern
results = analyze_api_logs("charging_station_logs_2025*.csv", "dict")
```

### Interactive Chart Generation

When running the script directly, it will prompt you after showing results:

```
Would you like to generate visualization charts? (y/N): y
```

### Output Formats

- **`"pretty"`**: Formatted console output with clear sections
- **`"json"`**: JSON formatted output for external processing
- **`"dict"`**: Raw Python dictionary for programmatic use

## Sample Output

```
================================================================================
API LOG ANALYSIS RESULTS
================================================================================

ANALYSIS SUMMARY
   Analysis Date: 2025-09-17 15:30:45
   Files Analyzed: 3
   Date Range: 2025-09-15 16:02:40 to 2025-09-17 11:26:58
   Unique Endpoints: 1
   Total Records: 42

TODAY
--------------------------------------------------
   Total Requests: 15
   Success: 13 (86.7%)
   Failures: 2 (13.3%)

   RESPONSE TIME METRICS (ms)
   Average: 9,234
   Median: 7,155
   Min: 3,950
   Max: 91,273
   95th percentile: 20,001
   99th percentile: 91,273

   SUCCESS RESPONSE TIMES (ms)
   Average: 6,847
   Min: 3,950
   Max: 18,768

   FAILURE RESPONSE TIMES (ms)
   Average: 30,871
```

## Visualization Features

The tool generates a comprehensive dashboard with four charts:

1. **Success Rate Over Time**: Line chart showing success percentage by hour
2. **Response Time Distribution**: Histogram comparing success vs failure response times
3. **Average Response Time Over Time**: Trend line of response times by hour
4. **Request Counts by Time Period**: Bar chart showing success/failure counts across different periods

Charts are automatically saved as PNG files with timestamps (e.g., `api_log_analysis_20250917_153045.png`).

## Metrics Explained

### Request Metrics
- **Total Requests**: Total number of API calls
- **Success Count/Rate**: Number and percentage of successful requests
- **Failure Count/Rate**: Number and percentage of failed requests

### Response Time Metrics
- **Average**: Mean response time across all requests
- **Median**: 50th percentile response time
- **Min/Max**: Fastest and slowest response times
- **95th/99th Percentile**: Response times for 95% and 99% of requests
- **Success/Failure Averages**: Separate averages for successful and failed requests

### Time Periods
- **Today**: From midnight of current day
- **This Week**: From Monday of current week
- **This Month**: From 1st day of current month
- **Last 7 Days**: Rolling 7-day window
- **Last 30 Days**: Rolling 30-day window
- **All Time**: Complete dataset

## Function Parameters

```python
analyze_api_logs(csv_files_pattern="*.csv", output_format="json", generate_charts=False)
```

### Parameters
- **`csv_files_pattern`** (str): Glob pattern to match CSV files
  - Examples: `"*.csv"`, `"logs/*.csv"`, `"api_logs_2025*.csv"`
- **`output_format`** (str): Output format
  - `"pretty"`: Formatted console output
  - `"json"`: JSON string output
  - `"dict"`: Raw dictionary (default)
- **`generate_charts`** (bool): Whether to create visualization charts
  - `True`: Generate and save charts automatically
  - `False`: No chart generation (default)

### Returns
- **Dictionary**: Contains analysis results for all time periods plus summary information

## Project Structure

```
api-log-analyzer/
├── api_log_analyzer.py    # Main analysis function
├── README.md             # This file
├── requirements.txt      # Python dependencies
└── sample_logs/          # Example CSV files
    ├── api_logs_2025-09-15.csv
    ├── api_logs_2025-09-16.csv
    └── api_logs_2025-09-17.csv
```

## Error Handling

The analyzer handles common issues automatically:
- **Missing files**: Warns when no files match the pattern
- **Invalid timestamps**: Skips rows with unparseable dates
- **Missing data**: Handles null/empty values gracefully
- **File read errors**: Reports and skips problematic files
- **Empty datasets**: Returns zero-filled metrics for empty time periods
- **Chart generation errors**: Continues analysis even if visualization fails

## Example Integration

```python
import json
from datetime import datetime

# Analyze logs and generate charts
results = analyze_api_logs("production_logs_*.csv", "dict", generate_charts=True)

# Extract key metrics
today_success_rate = results['today']['success_rate']
avg_response_time = results['today']['avg_response_time_ms']

# Save results to file
with open(f'api_analysis_{datetime.now().strftime("%Y%m%d")}.json', 'w') as f:
    json.dump({k: v for k, v in results.items() if k != '_dataframe'}, f, indent=2, default=str)

# Print summary
print(f"Today's Success Rate: {today_success_rate:.1f}%")
print(f"Average Response Time: {avg_response_time:.0f}ms")

# Check if charts were generated
chart_files = glob.glob("api_log_analysis_*.png")
if chart_files:
    print(f"Charts saved: {', '.join(chart_files)}")
```

## Requirements File

Create a `requirements.txt` file with:
```
pandas>=1.3.0
numpy>=1.20.0
matplotlib>=3.3.0
seaborn>=0.11.0
```

Install with:
```bash
pip install -r requirements.txt
```

## Command Line Usage

Run directly from command line:
```bash
python api_log_analyzer.py
```

The script will:
1. Analyze all CSV files in the current directory
2. Display results in the terminal
3. Prompt if you want to generate charts
4. Save visualization files if requested

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - feel free to use this in your projects!

## Issues & Support

If you encounter any issues or have feature requests, please:
1. Check existing issues first
2. Provide sample CSV data (anonymized)
3. Include error messages and Python version
4. Describe expected vs actual behavior

---

**Happy API Monitoring!**