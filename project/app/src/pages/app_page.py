import json

from dash import html, dcc, Output, Input, register_page, callback, State
import folium

from src_code import accident

register_page(__name__, path='/app', title='app', order=2)

f_content = open('languages/en/app_page.json')
content = json.load(f_content)
f_content.close()


def layout():
    return html.Div([
        html.H1(content['title'], className='text-2xl font-bold'),
        html.Div([
            html.H2(content['card_1']['title'], className='text-lg'),
            html.P(content['card_1']['text']),
        ], className='card'),
        html.Div([
            html.Div([
                html.H2(content['card_2']['title'], className='text-lg'),
                html.Div(id='map'),
            ], className='card w-1/2 flex flex-col gap-4'),
            html.Div([
                html.H2(content['card_3']['title'], className='text-lg'),
                html.Div([
                    dcc.Input(
                        id="search_value",
                        type='text',
                        placeholder="Enter the location to search",
                        className='px-2 py-4 border-gray-500 border-2 rounded-md bg-transparent text-gray-200'
                    ),
                    html.Button(
                        'Search',
                        id='search_btn',
                        className='rounded-md bg-indigo-400 text-white shadow-md px-3 py-2'
                    ),
                    html.P('Results:'),
                    html.Hr(),
                    dcc.Loading(
                        type='default',
                        className='py-6',
                        children=[
                            html.Div([
                                html.P('Accident Point:', className='font-bold'),
                                html.P('', id='accident_point', className=''),
                                html.P('Possible Agents:', className='font-bold'),
                                html.Div('', id='possible_agents', className=''),
                                html.P('Best Agent:', className='font-bold'),
                                html.Div('', id='best_agent', className=''),
                            ])
                        ]
                    )
                ], className='flex flex-col gap-4 w-full'),
            ], className='card w-1/2 flex flex-col gap-4'),
        ], className='flex justify-between gap-10')
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
def cb_render(n_clicks, value):
    # Initialize variables for the outputs
    address, agents, agent_to_call, map_graph = None, None, None, None

    if n_clicks is not None and n_clicks > 0 and value is not None:
        accident_point, nearest_agents, best_agent = accident.main(value, real_agent=True)

        address = accident_point.address
        agents = [html.P(f'{agent.id} -> {agent.latitude}, {agent.longitude}')
                  for index, agent in nearest_agents.iterrows()]

        agent_to_call = html.P(f'{best_agent.id[0]} -> {best_agent.latitude[0]}, {best_agent.longitude[0]}')

        # TODO[1]: display best agent time
        # TODO[2]: make the page responsive
        # TODO[3]: add instructions
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
