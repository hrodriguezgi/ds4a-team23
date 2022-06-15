from dash import Dash
import dash_bootstrap_components as dbc

app = Dash(
    __name__,
    title='DS4A App',
    external_stylesheets=[dbc.icons.FONT_AWESOME],
)
