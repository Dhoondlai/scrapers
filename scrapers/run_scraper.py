#!/usr/bin/env python3
import os
import sys
import argparse
import importlib
import time
from datetime import datetime


def run_scraper(scraper_name):
    # Set environment variable to indicate local execution
    os.environ["IS_LOCAL"] = "True"

    # Ensure the current directory is in the Python path
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

    try:
        # Dynamically import the specified scraper module
        module_path = f"{scraper_name}"

        print("Module path: ", module_path)

        scraper_module = importlib.import_module(module_path)

        print("Scraper module: ", scraper_module)

        print(f"Running {scraper_name} scraper...")
        start_time = time.time()
        start_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"Start time: {start_datetime}")

        # Create mock event and context objects
        mock_event = {}
        mock_context = {}

        # Run the lambda function
        scraper_module.run(mock_event, mock_context)

        end_time = time.time()
        end_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        elapsed_seconds = end_time - start_time
        minutes = int(elapsed_seconds // 60)
        seconds = int(elapsed_seconds % 60)

        print(f"\n{scraper_name} scraper completed successfully.")
        print(f"Start time: {start_datetime}")
        print(f"End time: {end_datetime}")
        print(f"Total execution time: {minutes} minutes and {seconds} seconds")

    except ImportError:
        print(
            f"Error: Scraper '{scraper_name}' not found. Make sure it exists in the scrapers/ directory.")
        return 1
    except Exception as e:
        print(f"Error running {scraper_name} scraper: {str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run a scraper lambda function locally.")
    parser.add_argument(
        "scraper", nargs='?', help="Name of the scraper to run (e.g., junaidtech, techmatched)")
    parser.add_argument("--list", action="store_true",
                        help="List all available scrapers")

    args = parser.parse_args()

    if args.list:
        # List all available scrapers
        scrapers_dir = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), "")
        available_scrapers = [
            f[:-3] for f in os.listdir(scrapers_dir)
            if f.endswith('.py') and not f.startswith('__') and f != 'run_scraper.py'
        ]
        print("Available scrapers:")
        for scraper in available_scrapers:
            print(f"  - {scraper}")
        sys.exit(0)

    # Check if scraper name was provided
    if args.scraper is None:
        parser.print_help()
        print("\nError: You must specify a scraper name or use --list to see available scrapers.")
        sys.exit(1)

    # Run the specified scraper
    exit_code = run_scraper(args.scraper)
    sys.exit(exit_code)
