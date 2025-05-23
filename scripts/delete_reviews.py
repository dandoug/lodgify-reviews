"""
Delete a single review or all reviews
"""
import argparse
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).parent.parent))  # Add project root to Python path
# pylint: disable=wrong-import-position,import-error
from reviews.helpers import confirm_action, require_prop
from reviews.delete import delete_single_review, delete_all_reviews

if __name__ == "__main__":
    load_dotenv()  # Load props from .env

    # Define the command parser and parse the args
    parser = argparse.ArgumentParser(description="Delete a single review or all reviews")
    parser.add_argument("--review", type=int,
                        help="int32 id of review to delete, optional if deleting all")
    parser.add_argument("--prop", type=int,
                        default=os.getenv("PROP_ID"),
                        help="int32 id of property, ignored if --review is not specified, " +
                             "defaults to PROP_ID env var")
    args = parser.parse_args()

    if args.review:
        # Single review delete
        review_id = args.review
        prop_id = require_prop(args)

        print(f"Deleting single review: {review_id} using prop_id: {prop_id}")
        delete_single_review(review=review_id, prop=prop_id)
    else:
        # Bulk delete for the account
        print("Deleting all reviews for account")
        if confirm_action():  # deleting all is pretty destructive, double check
            delete_all_reviews()
        else:
            print("Aborting")
