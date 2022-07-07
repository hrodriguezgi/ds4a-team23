from dash import Dash, html, page_container
import dash_bootstrap_components as dbc
from components import sidebar


# Instantiate the Dash Application
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

# Expose the server for production
server = app.server

# Create the main container for the different pages
content = html.Div([
    page_container
], className='overflow-auto w-full h-full px-2 py-10 lg:p-10 flex flex-col gap-10', id='content')

# Create the main layout of the app
app.layout = html.Div([
    html.Div([
        sidebar.create(),
    ]),
    content,
], className='flex flex-nowrap w-full h-screen overflow-hidden bg-slate-900')


if __name__ == '__main__':
    app.run(
        debug=True,
        host='localhost',
        port=8050,
    )
