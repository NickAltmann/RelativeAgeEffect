import unittest
from urlparse import urlparse
import os
import requests
import relative_age.http_access


class HttpTest(unittest.TestCase):
    def setUp(self):
        relative_age.http_access.get_hmtl = caching_request


def caching_request(url, params=None):
    text = get_from_file(url, params)
    if not text:
        text = write_to_file(url, params)
    return text


def get_from_file(url, params):
    """Mock for http get to be used in unittests."""
    filename = filename_from_url(url, params)
    if not os.path.isfile(filename):
        return None

    with open(filename, 'r') as f:
        text = f.read().decode('utf8')

    return text


def write_to_file(url, params):
    text = requests.get(url, params).text.encode('utf8')
    filename = filename_from_url(url, params)
    dirname = os.path.dirname(filename)
    if not os.path.isdir(dirname):
        os.makedirs(dirname)

    with open(filename, 'w') as f:
        f.write(text)

    return text


def filename_from_url(url, params):
    parsed = urlparse(url)
    dir = parsed.netloc.replace('/', '_')
    file_section = parsed.path.replace('/', '_')
    param_section = ('_' + '_'.join(['%s=%s' % (k, params[k] if params[k] else str(k)) for k in sorted(params.keys())])) if params else ''

    return os.path.join(os.path.dirname(__file__), 'data', dir, file_section + param_section)



if __name__ == "__main__":
    HttpTest.recording = True
    cases = unittest.TestLoader().discover(os.path.dirname(__file__))
    result = unittest.TestResult()
    result.shouldStop = False
    cases.run(result)
    #run_http_tests(cases)
    """
    url_list = ["http://www.footballsquads.co.uk/eng/2015-2016/",
                "http://www.footballsquads.co.uk/eng/2015-2016/faprem/",
                "http://www.footballsquads.co.uk/eng/2015-2016/faprem/wba.htm",
                ]

    for url in url_list:
        write_to_file(url)
    """
