import pandas as pd

import plotly.graph_objs as go


def training_type(weekday):
    if weekday == 1:
        return 'LONG'
    if weekday == 5:
        return 'HARD'
    if weekday in [3, 6]:
        return 'EASY'
    return 'OTHER'


class StatProvider:
    def __init__(self):
        self.trainings = pd.read_hdf('data/mama_to_use.hdf')
        self.cities = pd.read_csv('data/cities_final.csv')

        self.trainings['training_type'] = self.trainings['date'].dt.dayofweek.apply(training_type)
        self.trainings['dur_mins'] = self.trainings['duration'].dt.total_seconds() / 60
        self.trainings['daysfromstart'] = (self.trainings['date'] - self.trainings['date'].min()).dt.days

    def km_done(self):
        return self.trainings['distance'].sum()

    def current_city(self):
        visited_cities = self.cities[self.cities['distance'] <= self.km_done()]
        return visited_cities[visited_cities['distance'] == visited_cities['distance'].max()].iloc[0]

    def next_city(self):
        cities_to_visit = self.cities[self.cities['distance'] > self.km_done()]
        if cities_to_visit.shape[0] == 0:
            return 'WSZYSTKIE ODWIEDOZNE', 0
        else:
            return cities_to_visit[cities_to_visit['distance'] == cities_to_visit['distance'].min()].iloc[0]

    def number_of_trainings(self):
        return self.trainings.shape[0]

    def total_time(self):
        return str(self.trainings['duration'].sum()).replace('days', 'dni').split('.')[0]

    def sierpc_travels(self):
        return self.km_done() / 38.6

    def total_calories(self):
        return self.trainings['calories'].sum()

    def burgers_burnt(self):
        return self.total_calories() / 294

    def average_speed(self):
        return (self.trainings['distance'].sum() / self.trainings['duration'].sum().total_seconds()) * 3600

    def weekly_stats(self):
        self.trainings['weeknum'] = (self.trainings['daysfromstart'] - 2) // 7
        dates = self.trainings.groupby('weeknum')['date'].max().astype(str)
        return self.trainings.groupby('weeknum')[['distance', 'calories']].sum(), dates

    def scatterplot_fig(self):

        color_start = 40
        multiplier = 1.6

        df_easy = self.trainings[self.trainings['training_type'] == 'EASY']
        df_hard = self.trainings[self.trainings['training_type'] == 'HARD']
        df_long = self.trainings[self.trainings['training_type'] == 'LONG']
        data = [
                   go.Scatter(
                       x=[df_easy['dur_mins'].iloc[i]],
                       y=[df_easy['calories'].iloc[i]],
                       name='ŁATWY',
                       mode='markers',
                       marker={
                           'size': 15,
                           'color': 'rgba(20, {}, 20, .7)'.format(
                               int(color_start + df_easy['daysfromstart'].iloc[i] * multiplier)),
                           'line': {'width': 2}
                       },
                       showlegend=i == df_easy.shape[0] - 1
                   ) for i in range(df_easy.shape[0])] + [
                   go.Scatter(
                       x=[df_hard['dur_mins'].iloc[i]],
                       y=[df_hard['calories'].iloc[i]],
                       name='TRUDNY',
                       mode='markers',
                       marker={
                           'size': 15,
                           'color': 'rgba({}, 20, 20, .7)'.format(
                               int(color_start + df_hard['daysfromstart'].iloc[i] * multiplier)),
                           'line': {'width': 2}
                       },
                       showlegend=i == df_hard.shape[0] - 1
                   ) for i in range(df_hard.shape[0])] + [
                   go.Scatter(
                       x=[df_long['dur_mins'].iloc[i]],
                       y=[df_long['calories'].iloc[i]],
                       name='DŁUGI',
                       mode='markers',
                       marker={
                           'size': 15,
                           'color': 'rgba(20, 20, {}, .7)'.format(
                               int(color_start + df_long['daysfromstart'].iloc[i] * multiplier)),
                           'line': {'width': 2}
                       },
                       showlegend=i == df_long.shape[0] - 1
                   ) for i in range(df_long.shape[0])
               ]

        layout = dict(title='Treningi w zależności od rodzaju',
                      xaxis=dict(zeroline=False, title='długość'),
                      yaxis=dict(zeroline=False, title='spalone kalorie')
                      )

        fig = dict(data=data, layout=layout)
        return fig
