"""
Helper functions for lodgify-reviews
"""
import os


def confirm_action(prompt="Are you sure? (y/N): ") -> bool:
    """
    Prompts the user for confirmation and returns a boolean based on the response.
    The function continuously asks for input until a valid response ('y', 'yes',
    'n', 'no', or an empty input) is provided. Input is case-insensitive and
    whitespaces are ignored. An empty input defaults to "no".

    :param prompt: A string representing the message to show to the user. Defaults
                   to "Are you sure? (y/N): ".
    :type prompt: str
    :return: A boolean value where True represents a "yes" confirmation and False
             represents a "no" confirmation or an empty input.
    :rtype: bool
    """
    while True:
        response = input(prompt).lower().strip()
        if response in ['y', 'yes']:
            return True
        if response in ['n', 'no', '']:  # Empty response means "no"
            return False
        print("Please answer 'y' or 'n'")


def build_headers(include_content_type: bool = True):
    """
    Build the headers used for Lodgify API requests
    """
    result = {
        'Authorization': f'Bearer {os.environ.get("AUTH_TOKEN")}',
        'Accept': 'application/json'
    }
    if include_content_type:
        result['Content-Type'] = 'application/json'
        result['Content-Encoding'] = 'utf-8'
    return result


def check_status_and_extract(response):
    """
    Checks the status of a response and extracts the JSON data if the request is successful.

    This function first verifies the HTTP status of the response object to ensure that the
    request was successful. It then parses the response body as JSON and checks for a
    `success` key in the data. If the key is not present or indicates a failure, an error
    message is raised.

    :param response: The HTTP response object to process.
    :type response: requests.Response
    :raises HTTPError: If the HTTP response status code indicates an error.
    :raises ValueError: If the JSON response data indicates the request was not successful.
    :return: Parsed JSON data from the response if the request was successful.
    :rtype: dict
    """
    response.raise_for_status()
    response_data = response.json()
    if not response_data.get('success'):
        raise ValueError(f"Request failed with message: {response_data.get('message')}")
    return response_data
