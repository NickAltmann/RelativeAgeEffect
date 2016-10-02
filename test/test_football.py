import relativeage.football
import http_from_file


class TestFootball(http_from_file.HttpTest):

    def get_squads(self):

        squads = relativeage.football.Squads()
        return squads

    def test_list_countries(self):

        squads = self.get_squads()
        countries = squads.list_countries()

        self.assertIn('england', countries)

    def test_season_code(self):

        squads = self.get_squads()

        self.assertEquals(squads._season_code(2015, True), "2015-2016")
        self.assertEquals(squads._season_code(2015, False), "2015")

    def test_div_links(self):
        season_link = "http://www.footballsquads.co.uk/eng/2015-2016/"
        squads = self.get_squads()

        links = squads._get_div_links_from_season_link(season_link)
        self.assertIn('faprem/', links)
        self.assertEquals(5, len(links))

    def test_club_links(self):

        div_link = "http://www.footballsquads.co.uk/eng/2015-2016/faprem/"
        squads = self.get_squads()

        links = squads._get_club_links_from_div_link(div_link)
        self.assertIn('wba.htm', links)
        self.assertEquals(len(links), 20)

    def test_club_page(self):

        club_link = "http://www.footballsquads.co.uk/eng/2015-2016/faprem/wba.htm"
        squads = self.get_squads()

        df = squads._get_player_info(club_link)
        self.assertIn('Nat', df.columns)
        self.assertIn('Date of Birth', df.columns)
        self.assertEquals(32, df.shape[0])

    def test_full(self):
        squads = self.get_squads()

        df = squads.get_country_players('austria', 2016)
        self.assertIn('Nat', df.columns)
        self.assertIn('DOB', df.columns)
        self.assertEquals(len(df['Club'].unique()), 10)
