import dash
import dash_core_components as dcc
import dash_html_components as html
import base64

from statProvider import StatProvider


def image_src_path(real_path):
    encoded_image = base64.b64encode(open(real_path, 'rb').read())
    return 'data:image/png;base64,{}'.format(encoded_image.decode())


sp = StatProvider()
cur_city, km_cur_city = sp.current_city()
next_city, km_next_city = sp.next_city()

# external JavaScript files
external_scripts = [
    'https://www.google-analytics.com/analytics.js',
    {'src': 'https://cdn.polyfill.io/v2/polyfill.min.js'},
    {
        'src': 'https://cdnjs.cloudflare.com/ajax/libs/lodash.js/4.17.10/lodash.core.js',
        'integrity': 'sha256-Qqd/EfdABZUcAxjOkMi8eGEivtdTkh3b65xCZL4qAQA=',
        'crossorigin': 'anonymous'
    }
]

# external CSS stylesheets
external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    {
        'href': 'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO',
        'crossorigin': 'anonymous'
    }
]

app = dash.Dash(__name__,
                external_scripts=external_scripts,
                external_stylesheets=external_stylesheets)

colors = {
    'background': '#121e21',
    'text': '#bad3d9',
    'value': '#e0eff2',
    'header': '#ffffcc'
}


def value_div(name, value, text=False, width='33%'):
    font_size = '23px' if text else '23px'
    return html.Div(children=[
        html.Div(value, style={'fontSize': font_size, 'color': colors['value']}),
        html.Div(name)

    ], style={'textAlign': 'center', 'columns': 1,

              'float': 'left',
              'width': width
              })


weekly_stats, weekly_dates = sp.weekly_stats()

# app = dash.Dash(__name__, external_stylesheets=external_stylesheets, )
app.layout = html.Div([
    html.Div([html.Img(
        src=image_src_path(f"cities_photos/{cur_city}/picture_{i}.jpg"),
        style={'width': '33%', 'marginTop': '10px'}
    ) for i in range(3)], style={'textAlign': 'center', }),

    html.H1(children=f'Jesteś w mieście {cur_city}', style={
        'textAlign': 'center',
        'fontSize': '40px',
        'color': colors['header']
    }),

    html.Div(id='city_info',
             children=[
                 value_div('Odległe o', f'{km_cur_city}km', width='33%'),
                 value_div('Łącznie przejechane', f'{sp.km_done()}km', width='33%'),
                 value_div('Następne miasto, odległe o {0:.2f}km'.format(km_next_city - sp.km_done()), next_city,
                           text=True, width='33%'),
             ], style={
            'color': colors['text'],
            'fontSize': '18px',
            'textAlign': 'center',
            'display': 'table',
            'clear': 'both',
            'width': '100%'
        }
             ),

    html.H1(children=f'Rezultaty treningów', style={
        'textAlign': 'center',
        'fontSize': '30px',
        'color': colors['header']
    }),

    html.Div(id='general_stats1',

             children=[
                 value_div('Liczba treningów', f'{sp.number_of_trainings()}', width='50%'),
                 value_div('Czas na rowerze', f'{sp.total_time()}', width='50%')
             ], style={
            'color': colors['text'],
            'fontSize': '18px',
            'textAlign': 'center',
            'width': '100%'
        }
             ),
    html.Div(id='general_stats2',

             children=[
                 value_div('Przejechane kilometry', f'{sp.km_done()}', width='50%'),
                 value_div('Przejazdy do Sierpca', '{0:.2f}'.format(sp.sierpc_travels()), width='50%')
             ], style={
            'color': colors['text'],
            'fontSize': '18px',
            'textAlign': 'center',
            'width': '100%'
        }
             ),
    html.Div(id='general_stats3',

             children=[
                 value_div('Spalone kalorie', f'{sp.total_calories()}', width='50%'),
                 value_div('Spalone hamburgery', '{0:.2f}'.format(sp.burgers_burnt()), width='50%')
             ], style={
            'color': colors['text'],
            'fontSize': '18px',
            'textAlign': 'center',
            'width': '100%'
        }
             ),
    html.H1(children=f'Postępy', style={
        'textAlign': 'center',
        'fontSize': '30px',
        'color': colors['header']
    }),

    html.Div([
        dcc.Graph(
            id='weekly_kms',
            figure={
                'data': [
                    {'x': weekly_dates.values, 'y': weekly_stats['distance'].cumsum().values, 'type': 'line'}
                ],
                'layout': {
                    'title': 'Suma przejechanych kilometrów'
                }
            },
            style={
                'margin': '10px'
            }
        ),
        dcc.Graph(
            id='weekly_calories',
            figure={
                'data': [
                    {'x': weekly_dates.values, 'y': weekly_stats['calories'].values, 'type': 'bar'}
                ],
                'layout': {
                    'title': 'Suma spalonych kalorii w tygodniu'
                }
            },
            style={
                'margin': '10px'
            }
        )
    ], style={'columns': 2}),

    html.Div([html.Div([
        dcc.Graph(
            figure={
                'data': [
                    {'x': weekly_dates.values, 'y': weekly_stats['distance'].values, 'type': 'bar'}
                ],
                'layout': {
                    'title': 'Suma przejechanych kilometrów w tygodniu'
                }
            },
            style={
                'margin': '10px',
                'height': '44%'
            }
        ),
        dcc.Graph(
            figure=sp.scatterplot_fig(),
            style={
                'margin': '10px',
                'height': '56%'
            }
        )
    ], style={'overflow': 'hidden', 'width': '100%'}),
        html.Img(
        src=image_src_path(f"mama_rower.png"),
        style={'margin': '10px', 'objectFit': 'contain', 'marginLeft': 'auto'}
    ),
    ], style={'display': 'flex', 'columns': 2, 'width': '100%', 'align': 'right'})

], style={'align': 'center', 'backgroundColor': colors['background']}
)

# style={'columns': 1})
if __name__ == '__main__':
    app.run_server()
