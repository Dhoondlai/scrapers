# Dhoondlai Scrapers

## Getting Started

### Prerequisites

- Python 3.12
- Required Python packages

  (install with `pip install -r requirements.txt`):

## Developing Scrapers

### Scraper Structure

Each scraper should be a Python module with a `run(event, context)` function that serves as the entry point. This structure makes the scrapers compatible with both AWS Lambda deployment and local execution.

Example scraper structure:

```python
# Sample scraper: example_scraper.py

def run(event, context):
    """
    Main entry point for the scraper.

    Args:
        event (dict): Event data (empty when running locally)
        context (object): Runtime information (empty when running locally)

    Returns:
        dict: Result of the scraper execution
    """
    print("Scraping example site...")

    # Your scraping logic here
    # ...

    return {
        "status": "success",
        "items_scraped": 10
    }
```

### Best Practices

1. Handle exceptions properly
2. Include logging for important steps
3. Check for the `IS_LOCAL` environment variable if your scraper needs to behave differently when run locally
4. Respect websites' robots.txt and implement rate limiting

## Running Scrapers Locally

The `run_scraper.py` script allows you to test scrapers locally before deployment.

First of all, make the script executeable:

```bash
chmod +x run_scraper.py
```

Note: You need to be in the `scrapers` directory, with appropiate venv to run the script.

### Listing Available Scrapers

To see all available scrapers:

```bash
./run_scraper.py --list
```

### Running a Specific Scraper

To run a specific scraper:

```bash
./run_scraper.py <scraper_name>
```

For example:

```bash
./run_scraper.py junaidtech
```

This will:

1. Set the `IS_LOCAL` environment variable to `True`
2. Import the specified scraper module
3. Call the `run()` function with empty event and context objects
4. Display the results in the console

To run all scrapers, you can use the `--all` flag:

```bash
./run_scraper.py --all
```
