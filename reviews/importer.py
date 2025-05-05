"""
Handle importing reviews
"""
# pylint: disable=invalid-name,too-many-instance-attributes,no-value-for-parameter
from dataclasses import dataclass
from typing import Dict, Any

import requests
from requests import RequestException

from reviews import TIMEOUT, API_BASE
from reviews.helpers import build_headers


@dataclass
class ReviewData:
    """Class representing review data to send to Logify API to create a review"""
    guestName: str
    guestEmail: str
    guestCountry: str
    guestType: str
    roomName: str
    propertyId: int
    rating: int
    stayDate: str
    title: str
    text: str
    source: str

    @classmethod
    def from_csv_row(cls, row: Dict[str, Any], prop: int) -> 'ReviewData':
        """
        Creates an instance of `ReviewData` from a row dictionary and a property ID.
        """
        return cls(
            guestName=row['reviewer_name'],
            guestEmail="",
            guestCountry="US",
            guestType="Group",
            roomName="",
            propertyId=prop,
            rating=int(row['rating']),
            stayDate=row['created_time'][:7],
            title=row['review_title'],
            text=row['review_text'],
            source=row['type']
        )

    @classmethod
    def from_json(cls, obj: Dict[str, Any]) -> 'ReviewData':
        """
        Create a ReviewData instance from the objects returned by download_all_reviews()
        """
        return cls(
            guestName=obj['guestName'],
            guestEmail=obj['guestEmail'] or '',
            guestCountry=obj['guestCountry'] or 'US',
            guestType=obj['guestType'] or 'Group',
            roomName=obj['roomName'] or '',
            propertyId=int(obj['propertyId']),
            rating=int(obj['rating']),
            stayDate=obj['stayDate'],
            title=obj['title'],
            text=obj['text'],
            source=obj['source']
        )

    def as_create_review_payload(self):
        """
        Build the create review payload object from the review data
        """
        return {
            "propertyId": self.propertyId,
            "review": {
                "rating": self.rating,
                "guestEmail": self.guestEmail,
                "guestCountry": self.guestCountry,
                "guestName": self.guestName,
                "guestType": self.guestType,
                "roomName": self.roomName,
                "stayDate": self.stayDate,
                "text": self.text,
                "title": self.title,
                "source": self.source
            }
        }


@dataclass
class ReviewImportResult:
    """
    Hold the result for each review import attempt.
    """
    data: ReviewData
    status_code: int
    success: bool = False
    id: int = None
    message: str = ''


def import_reviews(reviews: list[ReviewData]) -> list[ReviewImportResult]:
    """
    Sort and then import a list of review data objects
    :param reviews:
    :return:
    """
    results = []
    # we always need to sort reviews by stayDate.  We want to sort in increasing
    # order by stayDate, so the most recent stays are the latest reviews added
    sorted_reviews = sorted(reviews, key=lambda x: x.stayDate)

    with requests.Session() as session:
        session.headers.update(build_headers())

        for review in sorted_reviews:
            try:
                url = f"{API_BASE}/v4/property/{review.propertyId}/reviews"
                response = session.post(url,
                                        json=review.as_create_review_payload(),
                                        timeout=TIMEOUT)
                result = ReviewImportResult(
                    data=review,
                    status_code=response.status_code)
                if response.status_code == 200:
                    response_data = response.json()
                    result.success = response_data.get('success', False)
                    result.id = response_data.get('data', {}).get('reviewId', None)
                    result.message = response_data.get('message', '')
                else:
                    result.success = False
                    result.id = None
                    result.message = response.text
                results.append(result)

            except requests.JSONDecodeError as e:
                raise ValueError("Invalid JSON response from server") from e

            except RequestException as e:
                raise RequestException("Failed to fetch reviews") from e
    return results
