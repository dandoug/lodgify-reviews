"""
Get a single review or all reviews
"""
import argparse
import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
sys.path.append(str(Path(__file__).parent.parent))  # Add project root to Python path
# pylint: disable=wrong-import-position,import-error
from reviews.download import download_all_reviews, download_single_review

if __name__ == "__main__":
    load_dotenv()  # Load props from .env

    # Define the command parser and parse the args
    parser = argparse.ArgumentParser(description="Download a single review or all reviews")
    parser.add_argument("--review", type=int,
                        help="int32 id of review to download, optional if getting all")
    parser.add_argument("--prop", type=int,
                        default=os.getenv("PROP_ID"),
                        help="int32 id of property, ignored if --review is not specified, " +
                             "defaults to PROP_ID env var")
    parser.add_argument("--output", type=argparse.FileType('w'),
                        default=sys.stdout,
                        help="file to write downloaded reviews to, defaults to stdout")
    args = parser.parse_args()

    # Check if writing stdout and remember the name
    is_stdout = args.output is sys.stdout
    output_name = "stdout" if is_stdout else args.output.name

    try:
        if args.review:
            review_id = args.review
            prop_id = args.prop
            if not prop_id:
                # needs to either come from arg lien or default env var (.env)
                raise ValueError("prop_id missing")

            print(f"downloading single review: {review_id} " +
                  f"using prop_id: {prop_id} to {output_name}")
            data = download_single_review(review=review_id, prop=prop_id)
        else:
            print(f"downloading all reviews for account to {output_name}")
            data = download_all_reviews()

        # write out the results
        json.dump(data, args.output, indent=2)
    finally:
        if not is_stdout:
            # close the file as long as it's not stdout
            args.output.close()
