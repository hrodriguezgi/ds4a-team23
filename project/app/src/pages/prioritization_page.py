from dash import html, dcc, Output, Input, register_page, callback, State
import folium

from src_code import priority
from components import select_priority

register_page(__name__, path='/prioritize', title='Prioritize Claims', order=3)


def layout():
    return html.Div([
        html.H1('Prioritize agents', className='text-2xl font-bold'),
        html.Div([
            html.H2('Instructions', className='text-lg'),
            html.Ol([
                html.Li('Type each accident location in each search input (they can be exact or close enough to the '
                        'accident points).'),
                html.Li('Click the search button.'),
            ], className='list-decimal list-inside pl-2'),
        ], className='card'),
        html.Div([
            html.Div([
                html.H2('Map (it loads once it has valid data)', className='text-lg'),
                html.Div(id='map_prioritization'),
            ], className='card w-full lg:w-1/2 flex flex-col gap-4 order-last lg:order-first'),
            html.Div([
                html.H2('Accident Search', className='text-lg'),
                html.Div([
                    html.Div([
                        dcc.Input(
                            id="search_value_1",
                            type='text',
                            placeholder="First location (e.g. Calle 7 # 34-13)",
                            className='w-full custom-select-border'
                        ),
                        select_priority.create(id_property='priority_1'),
                    ], className='flex justify-center items-center gap-4 w-full h-full'),
                    html.Div([
                        dcc.Input(
                            id="search_value_2",
                            type='text',
                            placeholder="Second location (e.g. Calle 7 # 34-13)",
                            className='w-full custom-select-border'
                        ),
                        select_priority.create(id_property='priority_2'),
                    ], className='flex justify-center items-center gap-4 w-full h-full'),
                    html.Button(
                        'Search',
                        id='search_btn',
                        className='rounded-md bg-indigo-400 text-white shadow-md px-3 py-2'
                    ),
                    html.P('Results', className='text-xl font-semibold'),
                    html.Hr(),
                    dcc.Loading(
                        type='default',
                        className='',
                        children=[
                            html.Div(id='accident_1', className='pb-6 py-4'),
                            html.Hr(),
                            html.Div(id='accident_2', className='py-6'),
                        ]
                    )
                ], className='flex flex-col gap-4 w-full'),
            ], className='card w-full lg:w-1/2 flex flex-col gap-4'),
        ], className='flex flex-col lg:flex-row justify-between gap-10')
    ], className='mx-auto container space-y-6 h-full')


@callback(
    output={
        'accident_1': Output("accident_1", "children"),
        'accident_2': Output("accident_2", "children"),
        'map': Output('map_prioritization', 'children'),
    },
    inputs=[Input("search_btn", 'n_clicks')],
    state=[State("search_value_1", 'value'), State("search_value_2", 'value')],
)
def cb_render(n_clicks, value_1: str, value_2: str):
    # Initialize variables for the outputs
    results_1, results_2, map_graph = None, None, None

    if n_clicks is not None and n_clicks > 0 and value_1 is not None and value_2 is not None:
        processed_value_1 = value_1.replace('#', 'No')
        processed_value_2 = value_2.replace('#', 'No')

        accident_1, accident_2 = priority.main(
            address1=processed_value_1,
            address2=processed_value_2,
            priority1=1,
            priority2=2,
        )

        accident_point1, nearest_agents1, best_agent_1, priority1 = accident_1
        accident_point2, nearest_agents2, best_agent_2, priority2 = accident_2

        address_1 = accident_point1.address
        address_2 = accident_point2.address

        agents_1 = [html.P(f'{agent.id} -> {agent.latitude}, {agent.longitude}')
                    for index, agent in nearest_agents1.iterrows()]

        agents_2 = [html.P(f'{agent.id} -> {agent.latitude}, {agent.longitude}')
                    for index, agent in nearest_agents1.iterrows()]

        agent_to_call_1 = html.P(f'The agent {best_agent_1.id[0]} located at'
                                 f' ({best_agent_1.latitude[0]}, {best_agent_1.longitude[0]})'
                                 f' will take {best_agent_1.time[0]} to get to the accident.')
        agent_to_call_2 = html.P(f'The agent {best_agent_2.id[0]} located at'
                                 f' ({best_agent_2.latitude[0]}, {best_agent_2.longitude[0]})'
                                 f' will take {best_agent_2.time[0]} to get to the accident.')

        results_1 = [
            html.P('First accident', className='text-lg font-semibold mb-4'),
            html.Div([
                html.P('Accident Location:', className='font-bold'),
                html.P(address_1, className='mb-4'),
                html.P('Possible Agents:', className='font-bold'),
                html.Div(agents_1, className='mb-4'),
                html.P('Best Agent:', className='font-bold'),
                html.Div(agent_to_call_1, className='mb-4'),
            ]),
        ]

        results_2 = [
            html.P('Second accident', className='text-lg font-semibold mb-4'),
            html.Div([
                html.P('Accident Location:', className='font-bold'),
                html.P(address_2, className='mb-4'),
                html.P('Possible Agents:', className='font-bold'),
                html.Div(agents_2, className='mb-4'),
                html.P('Best Agent:', className='font-bold'),
                html.Div(agent_to_call_2, className='mb-4'),
            ]),
        ]

        map_graph = generate_map(
            accident_loc_1=accident_point1,
            best_agent_loc_1=best_agent_1,
            nearest_agents_locations_1=nearest_agents1,
            accident_loc_2=accident_point2,
            best_agent_loc_2=best_agent_2,
            nearest_agents_locations_2=nearest_agents2,
        )

    return {
        'accident_1': results_1,
        'accident_2': results_2,
        'map': map_graph,
    }


def generate_map(
        accident_loc_1, best_agent_loc_1, nearest_agents_locations_1,
        accident_loc_2, best_agent_loc_2, nearest_agents_locations_2,
):
    # Create the map centered in the accident location
    fig = folium.Map((accident_loc_1.geometry[0].y, accident_loc_1.geometry[0].x), zoom_start=13)

    # Add the accident market to the map
    folium.Marker(
        location=[accident_loc_1.geometry[0].y, accident_loc_1.geometry[0].x],
        tooltip='First Accident',
        icon=folium.Icon(color='red'),
    ).add_to(fig)

    folium.Marker(
        location=[accident_loc_2.geometry[0].y, accident_loc_2.geometry[0].x],
        tooltip='Second Accident',
        icon=folium.Icon(color='red'),
    ).add_to(fig)

    # Add all the nearest agents
    for index, agent in nearest_agents_locations_1.iterrows():
        folium.Marker(
            location=[agent.latitude, agent.longitude],
            tooltip=f'Agent -> {agent.id}',
        ).add_to(fig)

    for index, agent in nearest_agents_locations_2.iterrows():
        folium.Marker(
            location=[agent.latitude, agent.longitude],
            tooltip=f'Agent -> {agent.id}',
        ).add_to(fig)

    # Add the best agent
    folium.Marker(
        location=[best_agent_loc_1.latitude[0], best_agent_loc_1.longitude[0]],
        tooltip=f'Best agent first accident -> {best_agent_loc_1.id[0]}',
        icon=folium.Icon(color='darkblue', icon='star'),
    ).add_to(fig)

    folium.Marker(
        location=[best_agent_loc_2.latitude[0], best_agent_loc_2.longitude[0]],
        tooltip=f'Best agent second accident -> {best_agent_loc_2.id[0]}',
        icon=folium.Icon(color='darkblue', icon='star'),
    ).add_to(fig)

    fig.save('map_prioritization.html')

    return html.Iframe(
        srcDoc=open('map_prioritization.html', 'r').read(),
        width='100%',
        height='100%',
        className='h-[40rem] w-full border-gray-300 border-2 rounded-md'
    )
