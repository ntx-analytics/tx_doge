import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/about", name="About")

# About card
about_card = dcc.Markdown(
    """
    This app analyzes Texas state expenditure data by county for 2021. Use the dropdowns and search bar to filter
    expenditures by county, agency, or any keyword. Export the filtered table with the button.
    """
)

# Data card
data_card = dcc.Markdown(
    """
    Data is sourced from the Texas State Expenditures by County dataset (2021), hosted on GitHub.
    [GitHub Repository](https://github.com/ntx-analytics/txdoge_data)
    """
)

# Layout with cards in an accordion
layout = html.Div([
    html.H1("About This App"),
    dbc.Accordion([
        dbc.AccordionItem(about_card, title="About the App"),
        dbc.AccordionItem(data_card, title="Data Source")
    ], start_collapsed=True),
    dbc.Button("Back to Home", href="/", color="primary", className="mt-3")
])