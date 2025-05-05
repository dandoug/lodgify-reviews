"""
Delete reviews from Lodgify
"""
import requests
from requests import RequestException

from reviews import API_BASE, TIMEOUT
from reviews.download import download_all_reviews
from reviews.helpers import build_headers, check_status_and_extract


def delete_single_review(review, prop):
    """
    Deletes a single review from a property using the specified review ID and property ID.
    This function communicates with an external API endpoint and removes the provided
    review, if it exists and the request is successful.

    :param review: The unique identifier of the review to delete.
    :type review: str
    :param prop: The unique identifier of the property associated with the review.
    :type prop: str
    :return: None
    :raises ValueError: If the server response contains invalid JSON.
    :raises RequestException: If the request fails due to connectivity issues or an
        invalid request.
    """
    url = f"{API_BASE}/v3/property/{prop}/reviews/{review}"

    try:
        response = requests.delete(url,
                                   headers=build_headers(include_content_type=False),
                                   timeout=TIMEOUT)
        check_status_and_extract(response)

    except requests.JSONDecodeError as e:
        raise ValueError("Invalid JSON response from server") from e

    except RequestException as e:
        raise RequestException("Failed to fetch reviews") from e


def _delete_reviews(reviews: list[tuple[int, int]]) -> None:
    """
    Deletes a list of reviews from a given property. Each review is identified by a
    tuple containing the review ID and the associated property ID. The operation
    is accomplished through making DELETE requests to a specified API endpoint.

    If an error occurs during processing, relevant exceptions are raised. The function
    uses a session with updated headers and ensures API responses are checked for validity.

    :param reviews: A list of tuples where each tuple contains an integer review ID
                    and an integer property ID.
    :type reviews: list[tuple[int, int]]
    :return: None
    :raises ValueError: If the server returns invalid JSON.
    :raises RequestException: If fetching (DELETE) operations fail or encounter errors.
    """
    with requests.Session() as session:
        session.headers.update(build_headers(include_content_type=False))

        for review, prop in reviews:
            try:
                url = f"{API_BASE}/v3/property/{prop}/reviews/{review}"
                response = session.delete(url, timeout=TIMEOUT)
                check_status_and_extract(response)

            except requests.JSONDecodeError as e:
                raise ValueError("Invalid JSON response from server") from e

            except RequestException as e:
                raise RequestException("Failed to fetch reviews") from e


def delete_all_reviews():
    """
    Deletes all reviews associated with the account.

    This function retrieves all reviews for the account and, if reviews are found,
    proceeds to delete them by extracting relevant information such as review IDs
    and associated property IDs. The deletion process is carried out in bulk.

    :raises KeyError: If the response data structure does not contain the expected
                      keys such as 'count' or 'reviews'.
    """
    # get the list of all reviews for the account
    review_data = download_all_reviews()
    if review_data["count"] > 0:
        # extract the reviews as a list of (review_id, prop_id) tuples
        reviews = [(review['id'], review['propertyId']) for review in review_data['reviews']]
        # process the list
        _delete_reviews(reviews)
