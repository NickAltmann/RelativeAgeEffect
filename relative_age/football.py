# -*- coding: utf-8 -*-

import datetime
import pandas as pd
from bs4 import BeautifulSoup

import http_access

class Squads(object):
    '''
    Class for retrieving list of players in football squads.
    Source of Material is http://www.footballsquads.com. Material: © FootballSquads.com, 1999 - 2016, All Rights Reserved
    '''

    # The countries for which data is available, the country code for the league and nationality code for the players.
    # An improvement would be to auto-discover this information.
    countries = {'england': {'country_code': 'eng',
                             'nationality_code': 'eng',
                             'season_spans_years': True},
                 'france':  {'country_code': 'france',
                             'nationality_code': 'fra',
                             'season_spans_years': True},
                 'spain':  {'country_code': 'spain',
                            'nationality_code': 'esp',
                            'season_spans_years': True},
                 'germany':  {'country_code': 'ger',
                              'nationality_code': 'ger',
                              'season_spans_years': True},
                 'italy':  {'country_code': 'italy',
                            'nationality_code': 'ita',
                            'season_spans_years': True},
                 'scotland':  {'country_code': 'scots',
                               'nationality_code': 'sco',
                               'season_spans_years': True},
                 'austria': {'country_code': 'austria',
                             'nationality_code': 'aut',
                             'season_spans_years': True},
                 }

    # Central method for getting html to make mocking straightforward.
    @staticmethod
    def _get_hmtl(link):
        """Return result of GET on the given link"""
        return http_access.get_hmtl(link)

    def _get_club_links_from_div_link(self, div_link):
        """Retrieve a list of links to clubs from a division page"""
        html = self._get_hmtl(div_link)
        soup = BeautifulSoup(html, 'html.parser')
        return [li.a['href'] for li in soup.body.ul('li') if not li.a['href'][-1] == '/']

    def _get_div_links_from_season_link(self, season_link):
        """Gets links to division pages from a season page"""
        html = self._get_hmtl(season_link)
        soup = BeautifulSoup(html, 'html.parser')
        links = [li.a['href'] for li in soup.body.ul('li')]
        return [x for x in links if x[-1] == '/' and x[0] != '/' and not x.startswith('update')]

    def _get_player_info(self, link):
        """Gets the player information from a club page"""
        html = self._get_hmtl(link)
        soup = BeautifulSoup(html, 'html.parser')

        table = soup.find("div", id="main").table
        player_info = pd.read_html(unicode(table))[0]

        player_info.columns = player_info.iloc[0]
        nli = player_info.Number[player_info.Number=='Players no longer at this club']
        if not nli.empty:
            player_info = player_info.iloc[1:nli.index[0],:]
        else:
            player_info = player_info.iloc[1:,:]
        player_info = player_info[pd.notnull(player_info.Name)]

        player_info = player_info[['Name', 'Nat', 'Pos', 'Height', 'Weight', 'Date of Birth']]
        return player_info

    def _season_code(self, season_start_year, season_spans_years):
        '''The season code used in the link'''
        return "%d-%d" % (season_start_year, season_start_year + 1) if season_spans_years else str(season_start_year)

    def list_countries(self):
        return self.countries.keys()

    def get_country_players(self, country, season_start_year):
        country_code = self.countries[country]['country_code']
        nationality_code = self.countries[country]['nationality_code'].upper()
        season_span = self.countries[country]['season_spans_years']

        season = self._season_code(season_start_year, season_span)
        link = 'http://www.footballsquads.co.uk/%s/%s/' % (country_code, season)

        r = pd.DataFrame()
        for div_link in self._get_div_links_from_season_link(link):
            div_name = div_link.split('/')[0]
            full_div_link = link + div_link
            for club_link in self._get_club_links_from_div_link(full_div_link):
                club_name = club_link.split('.')[0]
                full_club_link = full_div_link + club_link
                df = self._get_player_info(full_club_link).dropna(subset=['Date of Birth'])
                df = df[df.Nat.str.lower() == nationality_code.lower()]
                df['Div'] = div_name
                df['Club'] = club_name
                r = r.append(df)

        r.loc[:,'DOB'] = r.loc[:,'Date of Birth'].map(lambda x : datetime.datetime.strptime(x, "%d-%m-%y").date())
        return r

_cache = {}
squads = Squads()
def get_country_players(country, season_start_year):
    try:
        df = _cache[(country, season_start_year)]
    except KeyError:
        df = squads.get_country_players(country, season_start_year)
        _cache[(country, season_start_year)] = df
    return df

def get_england(season_start_year):
    return get_country_players('england', season_start_year)

def get_france(season_start_year):
    return get_country_players('france', season_start_year)

def get_spain(season_start_year):
    return get_country_players('spain', season_start_year)

def get_germany(season_start_year):
    return get_country_players('germany', season_start_year)

def get_italy(season_start_year):
    return get_country_players('italy', season_start_year)

