from main_dash import app
from setup_dash import setup_layout


if __name__ == '__main__':
    app.layout = setup_layout()
    app.run_server(debug=True)
