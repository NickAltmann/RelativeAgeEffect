import requests


# Central method for getting html to make mocking straightforward.
def get_hmtl(link, params=None):
    """Return result of GET on the given link"""
    return requests.get(link, params).text
