from dash import html, register_page

register_page(__name__, path='/about-us', title='About us', order=4)


def layout():
    team = [
        {
            'image': 'https://avatars.githubusercontent.com/u/64153233?v=4',
            'name': 'David Felipe Mora Ramirez',
            'role': 'Data Scientist',
            'linkedin': 'https://www.linkedin.com/in/david-felipe-mora/',
            'github': 'https://github.com/DavidFM43',
        },
        {
            'image': 'https://avatars.githubusercontent.com/u/61999750?v=4',
            'name': 'Felix David Gomez Marin',
            'role': 'Data Scientist',
            'linkedin': 'https://www.linkedin.com/in/felix-david-gomez-marin/',
            'github': 'https://github.com/FelixDavid12',
        },
        {
            'image': 'https://avatars.githubusercontent.com/u/11781011?v=4',
            'name': 'Harvey Rodriguez Gil',
            'role': 'Data Scientist',
            'linkedin': 'https://www.linkedin.com/in/hrodriguezgi/',
            'github': 'https://github.com/hrodriguezgi',
        },
        {
            'image': 'https://ui-avatars.com/api/?name=Maria+Alvarez',
            'name': 'Maria Fernanda Alvarez',
            'role': 'Data Scientist',
            'linkedin': '',
            'github': '',
        },
        {
            'image': 'https://avatars.githubusercontent.com/u/103336617?v=4',
            'name': 'Sebastian Chavarriaga',
            'role': 'Data Scientist',
            'linkedin': 'https://www.linkedin.com/in/sebastian-c-0a0071219/',
            'github': 'https://github.com/schavar',
        },
        {
            'image': 'https://avatars.githubusercontent.com/u/25954466?v=4',
            'name': 'Victor Manuel Villamil Perez',
            'role': 'Data Scientist',
            'linkedin': 'https://www.linkedin.com/in/victorvillamil95/',
            'github': 'https://github.com/vmvillamilp',
        }
    ]

    return html.Div([
        html.H1('About Us', className='text-2xl font-bold'),
        html.Div([
            html.Div([
                html.Img(src=member['image'], className='rounded-full w-32 h-32'),
                html.Div([
                    html.P(f'{member["name"]}', className='font-bold'),
                    html.P(f'{member["role"]}'),
                    html.A('LinkedIn', href=member["linkedin"], className='text-blue-400 underline', target='_blank'),
                    html.A('GitHub', href=member["github"], className='text-blue-400 underline', target='_blank'),
                ], className='flex flex-col gap-2'),
            ], className='card w-full flex items-center gap-4')
            for member in team
        ], className='grid grid-cols-2 lg:grid-cols-3 gap-10')
    ], className='mx-auto container space-y-6')
