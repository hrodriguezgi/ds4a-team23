import json

from dash import html, dcc, Output, Input
import dash_bootstrap_components as dbc
from main_dash import app

from views import app_page, history_page, context_page


f_sidebar = open('languages/en/sidebar.json')
sidebar_content = json.load(f_sidebar)
f_sidebar.close()

sidebar = html.Div([
    html.H2('Logo', className='w-full h-28'),
    html.Hr(),
    dbc.Nav(
        [
            dbc.NavLink(
                [html.I(className=f'fa-solid {tab["icon"]}'), tab['text']],
                href=tab['href'],
                active='exact',
                class_name='flex items-center gap-4 w-full'
            )
            for tab in sidebar_content['tabs']
        ],
        vertical=True,
        className='flex flex-col w-full mt-10'
    ),
], className='w-96 shadow h-screen bg-slate-800')

content = html.Div([], className='overflow-auto w-full h-full p-10 flex flex-col gap-10', id='content')


def setup_layout():
    return html.Div([
        dcc.Location(id='url', pathname='/app'),
        sidebar,
        content,
    ], className='flex flex-nowrap w-full h-screen overflow-hidden bg-slate-900')


@app.callback(Output('content', 'children'), [Input('url', 'pathname')])
def render_page_content(pathname):
    if pathname == '/context':
        return context_page.get_page()
    elif pathname == '/history':
        return history_page.get_page()
    elif pathname == '/app':
        return app_page.get_page()
    elif pathname == '/about-us':
        return html.P('About Us')

    # If the user tries to reach a different page, return a 404 message
    return html.Div(
        [
            html.H1('404: Not found', className='text-danger'),
            html.Hr(),
            html.P(f'The pathname {pathname} was not recognised...'),
        ]
    )
