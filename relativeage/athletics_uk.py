from dateutil.relativedelta import relativedelta
import datetime
import collections
import pandas as pd
from bs4 import BeautifulSoup

import http_access

class AgeGroup(object):
    Sen = None
    U20 = 'U20'
    U17 = 'U17'
    U15 = 'U15'
    U13 = 'U13'


class Area(object):
    UK = None
    England = 91
    Scotland = 92
    Wales = 93
    NI = 94


# event labels are readable terms used throughout age-groups, eg SteepleChase, Discus
# event tags are used in web queries and may be age-group specific eg 1500SC, DT2k

event_groups = {'Sprints': ['100m', '200m', '300m', '400m', 'ShortHurdles', 'LongHurdles'],
                'Distance': ['800m', '1500m', '3000m', 'SteepleChase', '5000m', '10000m'],
                'Jumps': ['HighJump', 'PoleVault', 'LongJump', 'TripleJump'],
                'Throws': ['Shot', 'Discus', 'Hammer', 'Javelin']}

event_to_group = {event: group for group, event_list in event_groups.items() for event in event_list }

rank_is_ascending = {'Sprints': True,
                     'Distance': True,
                     'Jumps': False,
                     'Throws': False}


def event_tag_to_event_label(event_tag):
    event_tag_u = event_tag.upper()
    if event_tag_u[:2] == "SP":
        return "Shot"
    if event_tag_u[:2] == "DT":
        return "Discus"
    if event_tag_u[:2] == "HT":
        return "Hammer"
    if event_tag_u[:2] == "JT":
        return "Javelin"
    if event_tag_u == "HJ":
        return "HighJump"
    if event_tag_u == "LJ":
        return "LongJump"
    if event_tag_u == "TJ":
        return "TripleJump"
    if event_tag_u == "PV":
        return "PoleVault"
    if "SC" in event_tag:
        return "SteepleChase"
    if event_tag_u.startswith("400H") or event_tag_u.startswith("300H") :
        return "LongHurdles"
    if "H" in event_tag_u:
        return "ShortHurdles"
    if event_tag == "Mar":
        return "Mar"
    return "%dm" % int(event_tag_u)


events_set = {AgeGroup.Sen: {'M': ['100', '200', '400', '110H', '400H', '800', '1500',  '3000SC', '5000', '10000',
                                   'HJ', 'PV', 'LJ', 'TJ', 'SP7.26K', 'DT2K', 'HT7.26K', 'JT800'],
                             'W': ['100', '200', '400', '100HW', '400HW', '800', '1500',  '3000SCW', '5000', '10000',
                                   'HJ', 'PV', 'LJ', 'TJ', 'SP4K', 'DT1K', 'HT4K', 'JT600']},
              AgeGroup.U20: {'M': ['100', '200', '400', '110HU20M', '400H', '800', '1500',  '2000SC', '3000', '5000',
                                   'HJ', 'PV', 'LJ', 'TJ', 'SP6K', 'DT1.75K', 'HT6K', 'JT800'],
                             'W': ['100', '200', '400', '100HW', '400HW', '800', '1500',  '1500SCW', '3000', '5000',
                                   'HJ', 'PV', 'LJ', 'TJ', 'SP4K', 'DT1K', 'HT4K', 'JT600']},
              AgeGroup.U17: {'M': ['100', '200', '400', '100HU17M', '400HU17M', '800', '1500',  '1500SC', '3000',
                                   'HJ', 'PV', 'LJ', 'TJ', 'SP5K', 'DT1.5K', 'HT5K', 'JT700'],
                             'W': ['100', '200', '400', '80HU17W', '300HW', '800', '1500',  '1500SCW', '3000',
                                   'HJ', 'PV', 'LJ', 'TJ', 'SP3K', 'DT1K', 'HT3K', 'JT500']},
              AgeGroup.U15: {'M': ['100', '200', '400', '80HU15M', '800', '1500',  '3000',
                                   'HJ', 'PV', 'LJ', 'TJ', 'SP4K', 'DT1.25K', 'HT4K', 'JT600'],
                             'W': ['100', '200', '300', '75HU15W', '800', '1500', '3000',
                                   'HJ', 'PV', 'LJ', 'TJ', 'SP3K', 'DT1K', 'HT3K', 'JT500']},
              AgeGroup.U13: {'M': ['100', '200', '75HU13M', '800', '1500',
                                   'HJ', 'PV', 'LJ', 'TJ', 'SP3.25K', 'DT1K', 'JT400'],
                             'W': ['100', '200', '70HU13W', '800', '1500', '3000',
                                   'HJ', 'PV', 'LJ', 'TJ', 'SP2.72K', 'DT0.75K', 'HT3K', 'JT400']}
              }

all_tags = set([event for age_group, d in events_set.items() for sex, events in d.items() for event in events])
tag_to_event = {tag: event_tag_to_event_label(tag) for tag in all_tags}

event_tag_mapping = {age_group: {mw: {tag_to_event[tag]: tag for tag in tags} for mw, tags in data.items()} for age_group, data in events_set.items()}
def get_event_tag(event, sex, age_group):
    try:
        return event_tag_mapping[age_group][sex][event]
    except KeyError:
        return None


def get_event_tags(sex, age_group):
    return events_set[age_group][sex]


def get_group_event_tags(event_group, sex, age_group):
    event_tags = []
    for event in event_groups[event_group]:
        event_tag = get_event_tag(event, sex, age_group)
        if not event_tag is None:
            event_tags.append(event_tag)
    return event_tags

class DataQuery(object):

    _pot_url = r"http://www.thepowerof10.info/rankings/rankinglist.aspx"

    def __init__(self, event, men_or_women, year, age_group, area):
        self.__event = event
        self.__men_or_women = men_or_women
        self.__year = year
        self.__age_group = age_group
        self.__area = area


    def key(self):
        return self.__event, self.__men_or_women, self.__year, self.__age_group, self.__area


    def _form_pot_query_dict(self):
        """Forms the url of the relevant ranking page."""
        query = {}
        query['sex'] = 'M' if self.__men_or_women[0].lower() == 'm' else 'W'
        query['agegroup'] = self.__age_group if self.__age_group else "ALL"
        query['event'] = self.__event
        if self.__year:
            query['year'] = self.__year
        else:
            query['alltime'] = 'y'
        if self.__area:
            query['areaid'] = self.__area

        return query


    def _get_pot_page(self):
        query = self._form_pot_query_dict()
        html = http_access.get_hmtl(self._pot_url, query)
        return html


    @staticmethod
    def parse_date(ss):
        dt = datetime.datetime.strptime(ss, "%d.%m.%y")
        if dt > datetime.datetime.now():
            dt -= relativedelta(years=100)
        return dt.date()


    def _process_pot_frame(self, raw):
        header_row = pd.Index(raw[0]).get_loc('Rank')
        formed = raw.ix[header_row+1:,:].copy()
        formed.columns = raw.loc[header_row]
        formed = formed[['Rank', 'Perf', 'Name', 'DOB']]
        formed.loc[:,'Rank'] = pd.to_numeric(formed['Rank'], errors='coerce')
        formed = formed.dropna(subset=['Rank', 'DOB'])
        formed.loc[:,'DOB'] = formed.loc[:,'DOB'].map(lambda x : self.parse_date(x))
        return formed

    def get_data(self):
        html = self._get_pot_page()
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find("span", id="cphBody_lblCachedRankingList").table
        df = pd.read_html(unicode(table))[0]
        return self._process_pot_frame(df)


class DataFactory(object):

    def __init__(self):
        self._cache = {}

    @staticmethod
    def merge_on_perf(list_of_dfs, ascending):
        merged = pd.concat(list_of_dfs)

        def to_float(perf):
            bits = perf.split(':')
            secs = float(bits[-1])
            mins = float(bits[0]) if len(bits) == 2 else 0.
            return mins * 60. + secs

        def sort_by_perf(df, ascending):
            s = df['Perf'].apply(to_float).reset_index(drop=True).sort_values(ascending=ascending).index
            return df.reset_index(drop=True).reindex(s).reset_index(drop=True)

        sorted_df = sort_by_perf(merged, ascending).drop_duplicates(subset=['Name', 'DOB'], keep="first")
        sorted_df['Rank'] = range(1, sorted_df.shape[0] + 1)
        return sorted_df

    @staticmethod
    def merge_on_rank(list_of_dfs, max_rank=None):

        def refine(df, max_rank):
            #return df[df['Rank']<=max_rank] if max_rank else df
            return df[:max_rank] if max_rank else df

        merged = pd.concat([refine(df, max_rank) for df in list_of_dfs]).sort_values('Rank')

        return merged.drop_duplicates(subset=['Name', 'DOB'], keep="first")


    def get_data_by_tag(self, event_tag, men_or_women, year=None, age_group=None, area=None):
        query = DataQuery(event_tag, men_or_women, year, age_group, area)
        try:
            data = self._cache[query.key()]
        except KeyError:
            data = query.get_data()
            self._cache[query.key()] = data
        return data

    def get_data_by_event(self, event, men_or_women, year=None, age_group=None, area=None):
        event_tag = get_event_tag(event, men_or_women, age_group)
        return self.get_data_by_tag(event_tag, men_or_women, year, age_group, area)


    def get_data(self,
                 sex=None,
                 event=None,
                 event_group=None,
                 years=None,
                 age_group=None,
                 areas=None,
                 max_rank=None,
                 max_rows=None):

        def is_iterable(x):
            return isinstance(x, collections.Iterable) and not isinstance(x, basestring)

        dfs = []
        sexes = ["M", "W"] if sex is None else [sex]
        for sex in sexes:
            if event_group:
                event_tags = get_group_event_tags(event_group, sex, age_group)
            elif event:
                event_tags = [get_event_tag(event, sex, age_group)]
            else:
                event_tags = get_event_tags(sex, age_group)

            for tag in event_tags:
                area_list = areas if is_iterable(areas) else [areas]
                year_list = years if is_iterable(years) else [years]
                ascending = rank_is_ascending[event_to_group[tag_to_event[tag]]]
                area_dfs = [self.get_data_by_tag(tag, sex, year, age_group, area) for area in area_list for year in year_list]
                dfs.append(self.merge_on_perf(area_dfs, ascending))

        combined = self.merge_on_rank(dfs, max_rank)
        limited = combined[:max_rows] if max_rows else combined
        return limited
