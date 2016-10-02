from datetime import date
import unittest
import datetime
import os
import pandas as pd
import relativeage.analysis

class TestAnalysis(unittest.TestCase):

    def load_test_file(self):
        filename = os.path.join(os.path.dirname(__file__), "data", "austria_2016.csv")
        df =  pd.DataFrame.from_csv(filename, encoding='utf-8')
        df.loc[:,'Date of Birth'] = df.loc[:,'Date of Birth'].map(lambda x : datetime.datetime.strptime(x, "%Y-%m-%d").date())
        return df

    def test_count_by_month(self):
        df = self.load_test_file()

        count = relativeage.analysis.count_by_month(df['Date of Birth'])

        self.assertEquals(count[3], 24)

    def test_frequency_by_month(self):
        df = self.load_test_file()

        freq = relativeage.analysis.daily_freq_by_month(df['Date of Birth'])
        self.assertAlmostEqual(freq[3], 24 / 31. )

    def test_date_distance(self):

        self.assertEquals(relativeage.analysis.date_dist(date(2016, 1, 1), 1), 0)
        self.assertEquals(relativeage.analysis.date_dist(date(2016, 12, 31), 1), 365)

    def test_average_date_distance(self):
        df = self.load_test_file()

        average = relativeage.analysis.average_date_dist(df['Date of Birth'], 1)
        self.assertAlmostEqual(average, 164.225130890)

        average = relativeage.analysis.average_date_dist(df['Date of Birth'], 9)
        self.assertAlmostEqual(average, 175.314136126)

    def test_offset(self):
        df = self.load_test_file()

        average = relativeage.analysis.average_offset(df['Date of Birth'], 9)
        self.assertAlmostEqual(average, -7.310863874)

    def test_year_split(self):
        df = self.load_test_file()

        early, late = relativeage.analysis.year_split(df['Date of Birth'], 1)
        self.assertEquals(early, 111)
        self.assertEquals(late, 80)

    def test_year_split_percentage(self):
        df = self.load_test_file()

        percent = relativeage.analysis.year_split_percentage(df['Date of Birth'], 1)
        self.assertAlmostEqual(percent, 100 * 111 / 191.)

    def test_chi_squared_exact(self):
        s = pd.Series(reduce(lambda x,y: x+y,[[date(2016,k,1)] * int(v * 4)
                                              for k,v in relativeage.analysis.month_days.to_dict().items()]))
        self.assertAlmostEqual(relativeage.analysis.chi_squared(s), 1.0)

    def test_chi_squared_all_jan(self):
        s = pd.Series([date(2015,1,1)] * 100)
        self.assertAlmostEqual(relativeage.analysis.chi_squared(s), 0.0)

    def test_group_by_period(self):

        s = pd.Series([date(2015,8,31), date(2015,9,1)])

        x = relativeage.analysis.group_by_period(s, 1, 4)
        self.assertTrue(pd.Series([0,0,2,0]).equals(x))

        x = relativeage.analysis.group_by_period(s, 9, 4)
        self.assertTrue(pd.Series([1,0,0,1]).equals(x))
