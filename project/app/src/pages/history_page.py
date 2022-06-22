import json

import pandas as pd
from dash import html, dcc, register_page
import plotly.express as px

register_page(__name__, path='/history', title='history')

f_content = open('languages/en/history.json')
content = json.load(f_content)
f_content.close()


def layout():
    df = pd.DataFrame({'lat': [4.651981275958889], 'lon': [-74.07677205983546]})

    fig = px.scatter_mapbox(df, lat="lat", lon="lon", zoom=10)
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    return html.Div([
        html.H1(content['title'], className='text-2xl font-bold'),
        html.Div([
            html.H2(content['card_1']['title'], className='text-lg'),
            html.P(content['card_1']['text']),
        ], className='card'),
        html.Div([
            html.Div([
                html.H2(content['card_2']['title'], className='text-lg'),
                html.Div(
                    dcc.Graph(figure=fig, className='h-[40rem] w-full border-gray-300 border-2 rounded-md'),
                    className=''
                ),
            ], className='card w-full flex flex-col gap-4'),
        ], className='h-full'),
    ], className='mx-auto container space-y-6 h-full')
