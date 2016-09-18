import unittest
import os
import http_from_file


class TestHttpFromFile(unittest.TestCase):
    def test_file_name_from_url_no_params(self):
        url = "http://www.footballsquads.co.uk/eng/2015-2016/faprem/arsenal.htm"
        params = None
        path = http_from_file.filename_from_url(url, params)
        rel_path = os.path.relpath(path, os.path.dirname(__file__))
        self.assertEquals(rel_path, r'data\www.footballsquads.co.uk\_eng_2015-2016_faprem_arsenal.htm')


    def test_file_name_from_url_with_params(self):
        url = "http://www.thepowerof10.info/rankings/rankinglist.aspx"
        params = {"event": "DT1.25K",
                  "agegroup": "U15",
                  "sex": "M",
                  "year": "2015"}
        path = http_from_file.filename_from_url(url, params)
        rel_path = os.path.relpath(path, os.path.dirname(__file__))
        self.assertEquals(rel_path, r'data\www.thepowerof10.info\_rankings_rankinglist.aspx_agegroup=U15_event=DT1.25K_sex=M_year=2015')

