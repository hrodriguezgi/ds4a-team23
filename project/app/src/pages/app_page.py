import json

import pandas as pd
from dash import html, dcc, Output, Input, register_page, callback
import plotly.express as px

from src_code import accident as acc

register_page(__name__, path='/app', title='app', order=2)

f_content = open('languages/en/app_page.json')
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
            ], className='card w-1/2 flex flex-col gap-4'),
            html.Div([
                html.H2(content['card_3']['title'], className='text-lg'),
                html.Div([
                    dcc.Input(
                        id="test",
                        type='text',
                        placeholder="Enter the location to search",
                        className='px-2 py-4 border-gray-500 border-2 rounded-md bg-transparent text-gray-200'
                    ),
                    html.Button('Search', className='rounded-md bg-indigo-400 text-white shadow-md px-3 py-2'),

                    html.P('Data to display:'),
                    html.Hr(),
                    html.P(id='output')
                ], className='flex flex-col gap-4 w-full'),
            ], className='card w-1/2 flex flex-col gap-4'),
        ], className='flex justify-between gap-10')
    ], className='mx-auto container space-y-6 h-full')


@callback(Output("output", "children"), Input("test", "value"))
def cb_render(value):
    acc.main(value, real_agent=True)
    return value
