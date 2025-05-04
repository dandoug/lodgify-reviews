"""
Helper functions for lodgify-reviews
"""


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
