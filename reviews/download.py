"""
Methods for downloading reviews from Lodgify
"""
from typing import Dict, List, Any
import requests
from requests.exceptions import RequestException
from reviews import API_BASE, TIMEOUT
from reviews.helpers import build_headers, check_status_and_extract

MAX_PAGE_SIZE = 5000
MAX_PAGES = 1000  # Reasonable limit to prevent infinite loops


def download_all_reviews() -> Dict[str, Any]:
    """
    Downloads all reviews in a paginated manner from the API endpoint.
    
    :return: A dictionary containing the count of retrieved reviews and a list of
        review data dictionaries.
    :raises RequestException: If there are network or API-related errors
    :raises ValueError: If the API response is invalid
    """
    page_spec = {
        "page": 1,
        "size": MAX_PAGE_SIZE
    }
    url = f"{API_BASE}/v3/property/reviews"
    results: List[Dict[str, Any]] = []

    with requests.Session() as session:
        session.headers.update(build_headers())

        for _ in range(MAX_PAGES):
            try:
                response = session.post(
                    url,
                    timeout=TIMEOUT,
                    json=page_spec
                )
                response_data = check_status_and_extract(response)

                items = response_data.get('data', {}).get('items', [])
                if not items:
                    break

                results.extend(items)
                page_spec["page"] += 1

            except requests.JSONDecodeError as e:
                raise ValueError("Invalid JSON response from server") from e
            except RequestException as e:
                raise RequestException("Failed to fetch reviews") from e

    return {
        "count": len(results),
        "reviews": results
    }


def download_single_review(review, prop):
    """
    Downloads a single review for a specified property. The function makes an HTTP
    GET request to fetch the review data, processes the response, and extracts
    the relevant information to return it. A list of reviews along with their count
    is returned.

    :param review: ID of the review to be downloaded
    :type review: str
    :param prop: ID of the property associated with the review
    :type prop: str
    :return: A dictionary containing the count of reviews and the list of reviews
    :rtype: dict
    :raises RequestException: If there is an issue with the HTTP request
    :raises ValueError: If the server returns an invalid JSON response
    """
    url = f"{API_BASE}/v3/property/{prop}/reviews/{review}"
    results: List[Dict[str, Any]] = []
    try:
        response = requests.get(url,
                                headers=build_headers(include_content_type=False),
                                timeout=TIMEOUT)
        response_data = check_status_and_extract(response)

        review_data = response_data.get('data', {})

    except requests.JSONDecodeError as e:
        raise ValueError("Invalid JSON response from server") from e

    except RequestException as e:
        raise RequestException("Failed to fetch reviews") from e

    if review_data:
        results.append(review_data)

    return {
        "count": len(results),
        "reviews": results
    }
