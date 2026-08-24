# Wikimedia Commons Image Scraper

A Python script to fetch image metadata from Wikimedia Commons for a given keyword, with pagination support and a batch size of 5 images per page.

## Features

- **API-based scraping**: Uses the official Wikimedia Commons API (not web scraping)
- **Config-driven**: Configuration via YAML/JSON file for flexibility
- **Pagination support**: Control where results start with the offset parameter
- **Batch size**: Fixed at 5 images per page as specified
- **Retry logic**: Exponential backoff retry strategy for robust API handling
- **Pretty-printed output**: Human-readable text formatting with detailed metadata
- **Error handling**: Graceful error messages and logging
- **Flexible output**: Print to console or save to file

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Setup

1. **Clone or enter the repository**:
   ```bash
   cd github-copilot-training-lab
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

   This installs:
   - `requests` - HTTP library for API calls
   - `pyyaml` - YAML configuration file parsing
   - `urllib3` - Retry mechanism for robust requests

## Configuration

Create or edit `config.yaml` to configure the scraper:

```yaml
# Required: Search keyword for images
keyword: "butterfly"

# Optional: Pagination offset (default: 0)
offset: 0

# Optional: Batch size (fixed at 5 per specification)
batch_size: 5

# Optional: Output file path (default: stdout)
output_file: null

# Optional: Maximum retry attempts (default: 3)
max_retries: 3

# Optional: Request timeout in seconds (default: 10)
request_timeout: 10
```

### Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `keyword` | string | **required** | Search term for finding images |
| `offset` | integer | 0 | Number of results to skip (for pagination) |
| `batch_size` | integer | 5 | Results per page (fixed at 5) |
| `output_file` | string/null | null | File path for output (null = stdout) |
| `max_retries` | integer | 3 | API retry attempts on failure |
| `request_timeout` | integer | 10 | Seconds to wait for API response |

## Usage

### Basic Usage (Print to Console)

```bash
python wikimedia_scraper.py config.yaml
```

Example output:
```
==================================================
Wikimedia Commons Image Metadata Results
==================================================

Keyword: butterfly
Offset: 0
Batch Size: 5 images per page
Results Fetched: 5
Query Time: N/A
--------------------------------------------------

[1] Title: File:Example butterfly.jpg
    URL: https://upload.wikimedia.org/wikipedia/commons/...
    Uploader: ExampleUser
    Date: 2023-06-15 14:30:22

[2] Title: File:Another butterfly.png
    ...

==================================================
```

### Pagination Examples

**Search with offset (skip first 10 results)**:
```yaml
keyword: "butterfly"
offset: 10
```

**Multiple batches**:
```bash
# Get results 0-4
python wikimedia_scraper.py config.yaml

# Get results 5-9 (offset=5)
sed -i 's/offset: 0/offset: 5/' config.yaml
python wikimedia_scraper.py config.yaml

# Get results 10-14 (offset=10)
sed -i 's/offset: 5/offset: 10/' config.yaml
python wikimedia_scraper.py config.yaml
```

### Save to File

Edit `config.yaml`:
```yaml
keyword: "butterfly"
output_file: "results.txt"
```

Then run:
```bash
python wikimedia_scraper.py config.yaml
```

The results will be saved to `results.txt`.

## Output Format

Results are formatted as pretty-printed text with the following structure:

```
==================================================
Wikimedia Commons Image Metadata Results
==================================================

Keyword: [search term]
Offset: [pagination offset]
Batch Size: 5 images per page
Results Fetched: [count]
--------------------------------------------------

[1] Title: [filename]
    URL: [image URL]
    Uploader: [username]
    Date: [timestamp]
    Description: [description text (first 100 chars)]

[2] Title: [filename]
    ...

==================================================
```

## Error Handling

The script includes built-in error handling:

- **Network errors**: Automatically retries with exponential backoff
- **Invalid config**: Clear error messages for configuration issues
- **API failures**: Graceful error messages without crashing
- **File write errors**: Errors logged if output file cannot be written

All errors are logged with timestamps for debugging.

## Architecture

### Files

- **wikimedia_scraper.py**: Main script and orchestrator
- **config_validator.py**: Configuration file loading and validation
- **wikimedia_api_client.py**: Wikimedia Commons API client with retry logic
- **output_formatter.py**: Result formatting (pretty-printed text)
- **config.yaml**: Example configuration file
- **requirements.txt**: Python dependencies

### Key Components

1. **ConfigValidator**: Loads and validates YAML/JSON configuration
2. **WikimediaAPIClient**: Handles API communication with retry logic
3. **OutputFormatter**: Formats results as human-readable text
4. **WikimediaScraper**: Orchestrates the entire workflow

## Logging

The script outputs informational and error messages to help with troubleshooting:

```
2024-01-15 10:30:45,123 - INFO - Configuration loaded successfully
2024-01-15 10:30:45,234 - INFO - Starting search for keyword: 'butterfly'
2024-01-15 10:30:45,456 - INFO - Querying Wikimedia Commons API...
2024-01-15 10:30:46,789 - INFO - Found 5 results
2024-01-15 10:30:47,012 - INFO - Results written successfully
```

## Limitations

- **Batch size**: Fixed at 5 images per page per specification
- **API rate limits**: Wikimedia Commons enforces rate limits; the retry logic with backoff handles temporary throttling
- **Search scope**: Searches across all image namespaces on Wikimedia Commons
- **Result quality**: Results depend on available metadata on Wikimedia Commons

## Troubleshooting

### No results found
- Check the keyword spelling
- Verify the keyword exists on Wikimedia Commons
- Try a more general keyword (e.g., "nature" instead of a specific species)

### API timeout
- Increase `request_timeout` in config.yaml
- Check your internet connection
- Try again later if Wikimedia Commons is slow

### Permission denied (output_file)
- Ensure the output directory exists and is writable
- Check file permissions
- Try a different output path

### Configuration errors
- Verify config.yaml is valid YAML
- Ensure all required fields are present
- Check field types (offset should be an integer, not a string)

## Development

To extend or modify the scraper:

1. Edit `wikimedia_api_client.py` to add new API methods
2. Edit `output_formatter.py` to change output format
3. Edit `config_validator.py` to add new configuration options
4. Update `config.yaml` with new example settings

## License

This script is provided as-is for educational purposes.

## References

- [Wikimedia Commons API Documentation](https://commons.wikimedia.org/wiki/Special:ApiSandbox)
- [MediaWiki API Search Documentation](https://www.mediawiki.org/wiki/API:Search)
