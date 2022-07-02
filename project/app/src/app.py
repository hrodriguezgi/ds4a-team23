from dash import Dash, html, page_container
import dash_bootstrap_components as dbc
from components import sidebar


app = Dash(
    __name__,
    title='DS4A App',
    external_stylesheets=[dbc.icons.FONT_AWESOME],
    use_pages=True,
    meta_tags=[{
        'name': 'viewport',
        'content': 'width=device-width, initial-scale=1',
    }],
)

server = app.server

content = html.Div([
    page_container
], className='overflow-auto w-full h-full p-10 flex flex-col gap-10', id='content')

app.layout = html.Div([
    sidebar.create(),
    content,
], className='flex flex-nowrap w-full h-screen overflow-hidden bg-slate-900')


if __name__ == '__main__':
    app.run(
        debug=True,
        host='localhost',
        port=8050,
    )
