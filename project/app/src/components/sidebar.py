from dash import html, page_registry
import dash_bootstrap_components as dbc
import json

f_sidebar = open('languages/en/sidebar.json')
sidebar_content = json.load(f_sidebar)
f_sidebar.close()


def create():
    return html.Div([
        html.H2('Logo', className='w-full h-28'),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink(
                    [html.I(className=f'fa-solid {tab["icon"]}'), tab['text']],
                    href=page['relative_path'],
                    active='exact',
                    class_name='flex items-center gap-4 w-full'
                )
                for page, tab in zip(page_registry.values(), sidebar_content['tabs'])
            ],
            vertical=True,
            className='flex flex-col w-full mt-10'
        ),
    ], className='w-96 shadow h-screen bg-slate-800')
