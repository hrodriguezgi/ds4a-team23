import json

from dash import html, dcc, Output, Input, register_page, callback, State
import folium

from src_code import accident

register_page(__name__, path='/best-agent', title='Find the Best Agent', order=2)

f_content = open('languages/en/app_page.json')
content = json.load(f_content)
f_content.close()


def layout():
    return html.Div([
        html.H1('Find the Best Agent', className='text-2xl font-bold'),
        html.Div([
            html.H2('Instructions', className='text-lg'),
            html.Ol([
                html.Li('Type the accident location in the search input (it can be exact or close enough to the '
                        'accident point).'),
                html.Li('Click the search button.'),
            ], className='list-decimal list-inside pl-2'),
        ], className='card'),
        html.Div([
            html.Div([
                html.H2('Map (it loads once it has valid data)', className='text-lg'),
                html.Div(id='map'),
            ], className='card w-full lg:w-1/2 flex flex-col gap-4 order-last lg:order-first'),
            html.Div([
                html.H2('Accident Search', className='text-lg'),
                html.Div([
                    dcc.Input(
                        id="search_value",
                        type='text',
                        placeholder="Enter the location to search (e.g. Calle 7 # 34-13 or Titan)",
                        className='px-2 py-4 border-gray-500 border-2 rounded-md bg-transparent text-gray-200'
                    ),
                    html.Button(
                        'Search',
                        id='search_btn',
                        className='rounded-md bg-indigo-400 text-white shadow-md px-3 py-2'
                    ),
                    html.P('Results', className='text-xl font-semibold'),
                    html.Hr(),
                    dcc.Loading(
                        type='default',
                        className='py-6',
                        children=[
                            html.Div([
                                html.P('Accident Location:', className='font-bold'),
                                html.P('', id='accident_point', className='mb-4'),
                                html.P('Possible Agents:', className='font-bold'),
                                html.Div('', id='possible_agents', className='mb-4'),
                                html.P('Best Agent:', className='font-bold'),
                                html.Div('', id='best_agent', className='mb-4'),
                            ])
                        ]
                    )
                ], className='flex flex-col gap-4 w-full'),
            ], className='card w-full lg:w-1/2 flex flex-col gap-4'),
        ], className='flex flex-col lg:flex-row justify-between gap-10')
    ], className='mx-auto container space-y-6 h-full')


@callback(
    output={
        'accident': Output("accident_point", "children"),
        'agents': Output("possible_agents", "children"),
        'best_agent': Output("best_agent", "children"),
        'map': Output('map', 'children'),
    },
    inputs=[Input("search_btn", 'n_clicks')],
    state=[State("search_value", 'value')],
)
def cb_render(n_clicks, value: str):
    # Initialize variables for the outputs
    address, agents, agent_to_call, map_graph = None, None, None, None

    if n_clicks is not None and n_clicks > 0 and value is not None:
        processed_value = value.replace('#', 'No')

        accident_point, nearest_agents, best_agent = accident.main(processed_value)

        address = accident_point.address
        agents = [html.P(f'{agent.id} -> {agent.latitude}, {agent.longitude}')
                  for index, agent in nearest_agents.iterrows()]

        agent_to_call = html.P(f'The agent {best_agent.id[0]} located at'
                               f' ({best_agent.latitude[0]}, {best_agent.longitude[0]})'
                               f' will take {best_agent.time[0]} in get to the accident.')

        # TODO[2]: make the page responsive
        # TODO[4]: message when the map is not there
        # TODO[5]: add another page for the agents prioritization

        map_graph = generate_map(
            accident_loc=accident_point,
            best_agent_loc=best_agent,
            nearest_agents_locations=nearest_agents,
        )

    return {
        'accident': address,
        'agents': agents,
        'best_agent': agent_to_call,
        'map': map_graph,
    }


def generate_map(accident_loc, best_agent_loc, nearest_agents_locations):
    # Create the map centered in the accident location
    fig = folium.Map((accident_loc.geometry[0].y, accident_loc.geometry[0].x), max_zoom=15, zoom_start=14)

    # Add the accident market to the map
    folium.Marker(
        location=[accident_loc.geometry[0].y, accident_loc.geometry[0].x],
        tooltip='Accident',
        icon=folium.Icon(color='red'),
    ).add_to(fig)

    # Add all the nearest agents
    for index, agent in nearest_agents_locations.iterrows():
        folium.Marker(
            location=[agent.latitude, agent.longitude],
            tooltip=f'Agent -> {agent.id}',
        ).add_to(fig)

    # Add the best agent
    folium.Marker(
        location=[best_agent_loc.latitude[0], best_agent_loc.longitude[0]],
        tooltip=f'Best agent -> {best_agent_loc.id[0]}',
        icon=folium.Icon(color='darkblue', icon='star'),
    ).add_to(fig)

    fig.save('map.html')

    return html.Iframe(
        srcDoc=open('map.html', 'r').read(),
        width='100%',
        height='100%',
        className='h-[40rem] w-full border-gray-300 border-2 rounded-md'
    )
