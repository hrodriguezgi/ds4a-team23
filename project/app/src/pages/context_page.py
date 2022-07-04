import json
from dash import html, dcc, register_page
import plotly.express as px

register_page(__name__, path='/', title='Context', order=0)

f_content = open('languages/en/context.json')
content = json.load(f_content)
f_content.close()


def layout():
    colors = {
        'background': '#1E293B',
    }

    df = px.data.stocks()
    fig = px.line(df, x="date", y="GOOG", template='plotly_dark')
    fig.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
    )

    df_election = px.data.election()
    election_counts = df_election['winner'].value_counts().reset_index()
    fig_election = px.pie(election_counts, names='index', values='winner')
    fig_election.update_layout(
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
                html.H2(content['card_2']['title'], className='text-lg'),
                html.Div(
                    dcc.Graph(figure=fig, className='border-gray-300 border-2 rounded-md'),
                ),
            ], className='card w-full lg:w-1/2 flex flex-col gap-4'),
            html.Div([
                html.H2(content['card_3']['title'], className='text-lg'),
                html.Div(
                    dcc.Graph(figure=fig_election, className='border-gray-300 border-2 rounded-md'),
                ),
            ], className='card w-full lg:w-1/2 flex flex-col gap-4'),
        ], className='flex flex-col lg:flex-row justify-between gap-10')
    ], className='mx-auto container space-y-6')
