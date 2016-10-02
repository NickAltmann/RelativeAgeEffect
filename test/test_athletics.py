import http_from_file
import relativeage.athletics_uk as ath


class TestAthletics(http_from_file.HttpTest):
    def test_get_event_tag(self):
        self.assertEquals(ath.get_event_tag("Javelin", "M", "U15"), "JT600")
        self.assertEquals(ath.get_event_tag("ShortHurdles", "W", "U17"), "80HU17W")
        self.assertIsNone(ath.get_event_tag("SteepleChase", "M", "U13"))

    def test_get_data_sen(self):
        fac = ath.DataFactory()
        df = fac.get_data_by_tag('1500', 'M', '2015')
        self.assertEquals(df.iloc[0]['Name'], "Mohamed Farah")

        df2 = fac.get_data_by_event('1500m', 'M', '2015')
        self.assertTrue(df.equals(df2))

        self.assertSetEqual({'Name', 'Rank', 'Perf', 'DOB'}, set(df.columns))

    def test_get_data_age_group(self):
        fac = ath.DataFactory()
        df = fac.get_data_by_tag('HJ', 'W', '2015', ath.AgeGroup.U13)
        self.assertEquals(df.iloc[0]['Name'], "Ella Hannyngton")

    def test_get_data_discus(self):
        fac = ath.DataFactory()
        df = fac.get_data_by_event('Discus', 'M', '2015', ath.AgeGroup.U15)
        self.assertEquals(df.iloc[0]['Name'], "Jay Morse")

    def test_get_data_area(self):
        fac = ath.DataFactory()
        df = fac.get_data_by_event('100m', 'W', '2015', area=ath.Area.Scotland)
        self.assertEquals(df.iloc[0]['Name'], "Alisha Rees")

    def test_get_data_all_time(self):
        fac = ath.DataFactory()
        df = fac.get_data_by_event('800m', 'M')
        self.assertEquals(df.iloc[0]['Name'], "Sebastian Coe")

    def test_get_group_event_tags(self):
        tags = ath.get_group_event_tags("Sprints", "M", ath.AgeGroup.Sen)
        self.assertSetEqual({'100', '200', '400', '110H', '400H'}, set(tags))

        tags = ath.get_group_event_tags("Throws", "W", ath.AgeGroup.Sen)
        self.assertSetEqual({'SP4K', 'HT4K', 'JT600', 'DT1K'}, set(tags))

        tags = ath.get_group_event_tags("Jumps", "M", ath.AgeGroup.Sen)
        self.assertSetEqual({'HJ', 'TJ', 'LJ', 'PV'}, set(tags))

        tags = ath.get_group_event_tags("Distance", "W", ath.AgeGroup.Sen)
        self.assertSetEqual({'800', '1500', '5000', '10000', '3000SCW'}, set(tags))
