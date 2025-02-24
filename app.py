import dash
from dash import html
import dash_bootstrap_components as dbc

# Initialize the app with multi-page support
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], use_pages=True)

# Navigation bar with About link added
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Home", href="/")),
        dbc.NavItem(dbc.NavLink("Expenditure Table", href="/table")),
        dbc.NavItem(dbc.NavLink("About", href="/about")),  # New link
    ],
    brand="Texas State Expenditures",
    color="secondary",
    dark=True,
)

# Footer
footer = html.Footer(
    "2025 TX D.O.G.E | Built with Dash and hosted on Heroku",
    style={'textAlign': 'center', 'padding': '20px', 'backgroundColor': '#f8f9fa', 'marginTop': '20px'}
)

# Main layout
app.layout = dbc.Container([
    navbar,
    dash.page_container,
    footer
], fluid=True)

# For Heroku deployment
server = app.server

if __name__ == "__main__":
    app.run(debug=True)