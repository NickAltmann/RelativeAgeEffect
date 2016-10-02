from datetime import date
import calendar
import pandas as pd
import scipy.stats

months_def = {
    1: {'days': 31, 'season': 'winter'},
    2: {'days': 28.25, 'season': 'winter'},
    3: {'days': 31, 'season': 'spring'},
    4: {'days': 30, 'season': 'spring'},
    5: {'days': 31, 'season': 'spring'},
    6: {'days': 30, 'season': 'summer'},
    7: {'days': 31, 'season': 'summer'},
    8: {'days': 31, 'season': 'summer'},
    9: {'days': 30, 'season': 'autumn'},
    10: {'days': 31, 'season': 'autumn'},
    11: {'days': 30, 'season': 'autumn'},
    12: {'days': 31, 'season': 'winter'},
         }

months = pd.DataFrame(months_def).transpose()
month_days = months['days']
season_days = months.groupby(['season']).sum()


def count_by_month(s):
    months = s.map(lambda x: x.month)
    raw_count = months.value_counts().sort_index()
    return raw_count


def daily_freq_by_month(s):
    count = count_by_month(s)
    freq = count / month_days
    return freq


def date_dist(dob, term_start_month):
    dob_month = dob.month
    start_of_term = date(dob.year if term_start_month <= dob_month else dob.year - 1, term_start_month, 1)
    dist = dob - start_of_term
    return dist.days


def average_date_dist(s, term_start_month):
    distances = s.map(lambda x: date_dist(x, term_start_month))
    average = distances.mean()
    return average


def average_offset(s, term_start_month):
    """
    Number of days the average birthday is away from the centre of the year.
    Year starts on the given month.
    A negative number means the average is early in the year.
    """
    return average_date_dist(s, term_start_month) - (365.25 / 2)


def year_split(s, term_start_month):
    """
    Returns a tuple: (born in first half of year, born in second half of year)
    The year begins on the given month.
    """
    b = group_by_period(s, term_start_month, 2)
    return b[0], b[1]


def group_by_period(series, term_start_month, periods):
    """
    Returns a sequence of length periods, indexed the same.
    Represents the count of birthdays binned by that number of equal periods, starting on term month.
    So periods=2 would group into first and second halves of the year.
    """
    distances = series.map(lambda x: date_dist(x, term_start_month))
    bins = [x * 366 / periods for x in range(periods+1)]
    period_count = pd.cut(distances, bins, labels=range(periods), include_lowest=True).value_counts().sort_index()
    return period_count


def year_split_percentage(s, term_start_month):
    """
    Returns percentage born in first half of the year.
    The year begins on the given month.
    """
    early, late = year_split(s, term_start_month)
    return early * 100. / (early + late)


def plot_by_month(s, title="", filename=""):
    count = s.shape[0]
    freq = count_by_month(s)
    df = pd.DataFrame({'count': freq.values}, index=list(calendar.month_abbr)[1:13])
    pt = df.plot(kind='bar', title=" ".join([title, "(n=%s)" % count]))

    if filename:
        fig = pt.get_figure()
        fig.savefig(filename)


def chi_squared(s):
    count = count_by_month(s)
    expected = month_days / month_days.sum() * count.sum()
    return scipy.stats.chisquare(count, expected).pvalue


def summary_table(labels, data, start_month):
    results = [(d.shape[0],
                average_offset(d, start_month),
                year_split_percentage(d, start_month),
                float(group_by_period(d, start_month, 4)[0])/group_by_period(d, start_month, 4)[3]) for d in data]

    df = pd.DataFrame(results,
                      columns=['Count',
                               'Offset',
                               'First half percentage',
                               'First to fourth quarter ratio'],
                      index=labels)

    return df.round(2)
