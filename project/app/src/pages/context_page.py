import json
from dash import html, dcc, register_page

from src_code.insights import Insights

register_page(__name__, path='/', title='Context', order=0)

f_content = open('languages/en/context.json')
content = json.load(f_content)
f_content.close()


def layout():
    insights = Insights()

    insights_to_display = [
        insights.deaths_per_accident(),
        insights.injuries_per_accident(),
        insights.accidents_per_priority(),
        insights.biggest_accidents_per_location(),
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
            html.P("TracJam is a web app that helps the SDM by analyzing the data around the city's mobility and"
                   " improves how the entity is reacting to different road accidents"
                   " and how they can both prioritize and optimize the agents distribution around Bogota."),
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
        ], className='grid grid-cols-1 lg:grid-cols-2 gap-4 h-full')
    ], className='mx-auto container space-y-6')
