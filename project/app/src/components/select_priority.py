from dash import dcc


def create(id_property=None):
    """
    Main function to create the dropdown to manage the accident types for the priority
    """

    return dcc.Dropdown(
        [
            {
                'label': 'Crash', 'value': '1',
            },
            {
                'label': 'Death', 'value': '2',
            },
            {
                'label': 'Injured', 'value': '3',
            }
        ],
        id=id_property if id_property is not None else '',
        className='w-full h-full',
        style={
            'width': '10rem'
        },
        placeholder='Type',
        clearable=False,
        searchable=False
    )
