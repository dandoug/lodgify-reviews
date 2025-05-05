"""
Import a file of reviews but creating them one by one through the Lodgify API
"""
import argparse
import csv
import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
sys.path.append(str(Path(__file__).parent.parent))  # Add project root to Python path
# pylint: disable=wrong-import-position,import-error
from reviews.importer import ReviewData, import_reviews


def _report_results(results):
    # Report the results of the import
    for result in results:
        if result.success:
            print(f"created review {result.id} for title: {result.data.title} " +
                  f"by {result.data.guestName}")
        else:
            print(f"error: status: {result.status_code} message: {result.message} for " +
                  f"title: {result.data.title} by {result.data.guestName}")


if __name__ == "__main__":
    load_dotenv()  # Load props from .env

    # Define the command parser and parse the args
    parser = argparse.ArgumentParser(description="Import a file of reviews")
    parser.add_argument("--prop", type=int,
                        default=os.getenv("PROP_ID"),
                        help="int32 id of property, ignored for .json files, " +
                             "defaults to PROP_ID env var")
    parser.add_argument("--reviews", type=argparse.FileType('r'),
                        help="file containing reviews to import, either .csv or .json")
    args = parser.parse_args()

    try:
        if not args.reviews:
            # a file needs to be specified
            raise ValueError("input file missing")
        input_file_name = args.reviews.name

        if not input_file_name.endswith(".json") and not input_file_name.endswith(".csv"):
            raise ValueError("input file must be .csv or .json")

        if input_file_name.endswith(".csv"):
            prop_id = args.prop
            if not prop_id:
                # required with using .csv file
                # needs to either come from arg lien or default env var (.env)
                raise ValueError("prop_id missing")

            print(f"importing .csv input from {input_file_name} using prop_id: {prop_id}")
            # Read the .csv file and build up a list of review objects
            try:
                csv_reader = csv.DictReader(args.reviews)
                reviews = [ReviewData.from_csv_row(row, prop_id) for row in csv_reader]
            except csv.Error as e:
                raise ValueError(f"Error reading CSV file: {str(e)}") from e

        else:  # input_file_name.endswith(".json"):
            print(f"importing .json input from {input_file_name}")
            try:
                json_reviews = json.load(args.reviews).get('reviews', [])
                reviews = [ReviewData.from_json(review) for review in json_reviews]
            except json.JSONDecodeError as e:
                raise ValueError(f"Error reading JSON file: {str(e)}") from e

        print(f"importing {len(reviews)} reviews")
        import_results = import_reviews(reviews)
        _report_results(import_results)

    finally:
        args.reviews.close()
