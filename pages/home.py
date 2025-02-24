import dash
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/", name="Home")

layout = html.Div([
    html.H1("Welcome to Texas State Expenditures"),
    html.P("This dashboard provides insights into Texas government spending by county for 2021. Navigate to the Expenditure Table to explore the data interactively."),
    dbc.Button("View Expenditure Table", href="/table", color="primary", className="mt-3")
])