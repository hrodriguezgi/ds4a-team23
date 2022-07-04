from dash import html


def create(id_property=None):
    return html.Select(
        [
            html.Option('Type', value=None, disabled=True),
            html.Option('Crash', value='1'),
            html.Option('Injured', value='2'),
            html.Option('Death', value='3'),
        ],
        id=id_property if id_property is not None else '',
        className='py-2 px-2 custom-select-border bg-gray-800',
    )
