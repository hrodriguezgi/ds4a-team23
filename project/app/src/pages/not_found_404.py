from dash import register_page, html

register_page(__name__)


def layout():
    return html.Div(
        [
            html.H1('404: Not found', className='text-danger'),
            html.Hr(),
            html.P(f'The pathname was not recognised...', className='text-2xl font-bold'),
        ]
    )
