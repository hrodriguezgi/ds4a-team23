import json

from dash import html, dcc, register_page, Output, Input, callback
from src_code.insights import Insights


register_page(__name__, path='/insights', title='Insights', order=1)

f_content = open('languages/en/insights.json')
content = json.load(f_content)
f_content.close()

insights: Insights | None = None

colors = {
    'background': '#1E293B',
}


def layout():
    global insights

    insights = Insights()

    insights_to_display = [
        insights.biggest_accidents_per_type(),
        insights.accidents_per_vehicle_type(),
        insights.accidents_per_location(),
        insights.draw_incidents_map(),
        insights.draw_incidents_clusters_map()
    ]

    for _, fig, _ in insights_to_display:
        fig.update_layout(
            plot_bgcolor=colors['background'],
            paper_bgcolor=colors['background'],
            font_color='#ffffff'
        )

    html_insights = [
        html.Div([
            html.Div(
                dcc.Graph(figure=fig, className='h-full w-full border-gray-300 border-2 rounded-md'),
                className=''
            ),
            html.P(" & ".join(insight))
        ], className='card w-full flex flex-col gap-4')
        for data, fig, insight in insights_to_display
    ]

    return html.Div([
        html.H1(content['title'], className='text-2xl font-bold'),
        html.Div([
            html.H2(content['card_1']['title'], className='text-lg'),
            html.P(content['card_1']['text']),
        ], className='card'),
        html.Div([
            *html_insights,
            html.Div([
                html.Div([], className='w-full h-full', id='graph_slider_1'),
                html.P(content.get('slider')),
                html.Div([
                    dcc.Slider(
                        0, 23, 1,
                        value=10,
                        id='slider_graph_1'
                    ),
                ]),
                html.P('', id='insight_graph_1')
            ], className='card w-full flex flex-col gap-4'),
            html.Div([
                html.Div([], className='w-full h-full', id='graph_slider_2'),
                html.P(content.get('slider')),
                html.Div([
                    dcc.Slider(
                        0, 23, 1,
                        value=10,
                        id='slider_graph_2'
                    ),
                ]),
                html.P('', id='insight_graph_2')
            ], className='card w-full flex flex-col gap-4'),
        ], className='h-full grid grid-cols-1 lg:grid-cols-2 gap-4 h-full'),
    ], className='mx-auto container space-y-6 h-full')


@callback(
    output=[Output('graph_slider_1', 'children'), Output('insight_graph_1', 'children')],
    inputs=[Input('slider_graph_1', 'value')]
)
def update_graph_1(value):
    fig_to_return = None
    insight = ''

    if insights is not None:
        _, fig, insight = insights.accidents_per_zone_and_hour(hour=int(value))

        fig.update_layout(
            plot_bgcolor=colors['background'],
            paper_bgcolor=colors['background'],
            font_color='#ffffff'
        )

        fig_to_return = html.Div(
            dcc.Graph(figure=fig, className='h-full w-full border-gray-300 border-2 rounded-md'),
            className=''
        )

    return fig_to_return, " & ".join(insight)


@callback(
    output=[Output('graph_slider_2', 'children'), Output('insight_graph_2', 'children')],
    inputs=[Input('slider_graph_2', 'value')]
)
def update_graph_2(value):
    fig_to_return = None
    insight = ''

    if insights is not None:
        _, fig, insight = insights.accidents_per_hour(hour=int(value))

        fig.update_layout(
            plot_bgcolor=colors['background'],
            paper_bgcolor=colors['background'],
            font_color='#ffffff'
        )

        fig_to_return = html.Div(
            dcc.Graph(figure=fig, className='h-full w-full border-gray-300 border-2 rounded-md'),
            className=''
        )

    return fig_to_return, " & ".join(insight)
