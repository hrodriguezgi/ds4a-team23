import json

from dash import html, dcc, register_page
from src_code.insights import Insights


register_page(__name__, path='/insights', title='Insights', order=1)

f_content = open('languages/en/insights.json')
content = json.load(f_content)
f_content.close()


def layout():
    insights = Insights()

    insights_to_display = [
        insights.biggest_accidents_per_type(),
        insights.accidents_per_vehicle_type(),
        insights.accidents_per_location(),
        insights.accidents_per_zone_and_hour(hour=0),
        insights.accidents_per_hour(hour=0)
    ]

    colors = {
        'background': '#1E293B',
    }

    for _, fig, _ in insights_to_display:
        fig.update_layout(
            plot_bgcolor=colors['background'],
            paper_bgcolor=colors['background'],
            font_color='#ffffff'
        )

    return html.Div([
        html.H1(content['title'], className='text-2xl font-bold'),
        html.Div([
            html.H2(content['card_1']['title'], className='text-lg'),
            html.P(content['card_1']['text']),
        ], className='card'),
        html.Div([
            html.Div([
                html.Div(
                    dcc.Graph(figure=fig, className='h-full w-full border-gray-300 border-2 rounded-md'),
                    className=''
                ),
                html.P(" & ".join(insight))
            ], className='card w-full flex flex-col gap-4')
            for data, fig, insight in insights_to_display
        ], className='h-full grid grid-cols-1 lg:grid-cols-2 gap-4 h-full'),
    ], className='mx-auto container space-y-6 h-full')
