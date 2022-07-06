from dash import html, page_registry, callback, Output, Input, State
import dash_bootstrap_components as dbc
import json
from dash_svg import Svg, Path

content: dict = dict()


def create():
    load_content_text()
    return html.Div([
        mobile_icon(),
        main_sidebar()
    ], className='relative')


def main_sidebar():
    return html.Div([
        html.Div([
            html.Div([
                html.Div([
                    html.Img(
                        src='/assets/traffic-jam.png',
                        className='w-auto h-48 mx-auto'
                    ),
                ], className='h-48 w-full flex justify-center'),
                html.Hr(),
                dbc.Nav(
                    [
                        dbc.NavLink(
                            [html.I(className=f'fa-solid {tab.get("icon")}'), tab.get('text')],
                            href=page['relative_path'],
                            active='exact',
                            class_name='flex items-center gap-4 w-full'
                        )
                        for page, tab in zip(page_registry.values(), content.get('tabs', {}))
                    ],
                    vertical=True,
                    className='flex flex-col w-full mt-10'
                ),
            ]),
            html.Div([
                html.Button('EN', className='text-lg font-bold px-6 text-gray-400 font-semibold'
                                            'hover:bg-gray-700 transition ease-in-out'),
                html.Button('ES', className='text-lg font-bold px-6 text-gray-400 font-semibold'
                                            'hover:bg-gray-700 transition ease-in-out'),
            ], className='flex justify-center divide-x divide-gray-200 py-4')
        ], className='h-full w-full flex flex-col justify-between')
    ],
        className='w-1/2 lg:w-60 shadow-2xl'
                  ' lg:shadow h-screen z-20 bg-slate-800 fixed lg:static hidden lg:block',
        id='sidebar'
    )


def mobile_icon():
    return html.Button([
        Svg(
            [
                Path(d='M24 6h-24v-4h24v4zm0 4h-24v4h24v-4zm0 8h-24v4h24v-4z')
            ],
            viewBox='0 0 24 24',
            className='p-1.5 w-7 h-7 bg-gray-300 hover:bg-gray-300 rounded-md shadow-md cursor-pointer'
        ),
    ], className='fixed lg:hidden p-6 z-20 right-0', id='mobile_button')


@callback(
    output=[Output("sidebar", "className")],
    inputs=[Input("mobile_button", 'n_clicks')],
    state=[State("sidebar", 'className')],
)
def toggle_sidebar(n_clicks, className: str):
    sidebar_classes: list = className.split()

    if n_clicks is not None:
        if 'hidden' in sidebar_classes:
            sidebar_classes.remove('hidden')
        else:
            sidebar_classes.append('hidden')

    return [
        ' '.join(sidebar_classes)
    ]


def load_content_text():
    global content
    f_content = open('languages/en/sidebar.json')
    content = json.load(f_content)
    f_content.close()
