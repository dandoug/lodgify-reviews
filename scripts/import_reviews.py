"""
Import a file of reviews but creating them one by one through the Lodgify API
"""
import argparse
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
sys.path.append(str(Path(__file__).parent.parent))  # Add project root to Python path


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
            # file needs to be specified
            raise ValueError("input file missing")
        input_file_name = args.reviews.name

        if input_file_name.endswith(".csv"):
            prop_id = args.prop
            if not prop_id:
                # required with using .csv file
                # needs to either come from arg lien or default env var (.env)
                raise ValueError("prop_id missing")

            print(f"importing .csv input from {input_file_name} using prop_id: {prop_id}")
        elif input_file_name.endswith(".json"):
            print(f"importing .json input from {input_file_name}")
        else:
            raise ValueError("input file must be .csv or .json")
    finally:
        args.reviews.close()
