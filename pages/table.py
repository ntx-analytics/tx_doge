import dash
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
import pandas as pd
import plotly.graph_objects as go

dash.register_page(__name__, path="/table", name="Expenditure Table")

csv_url = "https://raw.githubusercontent.com/ntx-analytics/txdoge_data/41b25e1cf23d73cc0d99479643895aba7e50a472/Texas_State_Expenditures_by_County_-_2021_20250219.csv"
df = pd.read_csv(csv_url)
keep_columns = ['Fiscal Year', 'Agency Number', 'Agency Name', 'County', 'Major Spending Category', 'Amount']
available_columns = [col for col in keep_columns if col in df.columns]
df = df[available_columns].fillna('N/A')
df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)

county_dropdown = html.Div([
    dbc.Label("Select Counties", html_for="county_dropdown"),
    dcc.Dropdown(
        id="county-dropdown",
        options=[{'label': 'Select All', 'value': 'ALL'}] + [{'label': c, 'value': c} for c in sorted(df["County"].unique())],
        value=['ALL'],
        multi=True,
        clearable=False,
        maxHeight=600,
        optionHeight=50
    ),
], className="mb-4")

agency_dropdown = html.Div([
    dbc.Label("Select Agencies", html_for="agency_dropdown"),
    dcc.Dropdown(
        id="agency-dropdown",
        options=[{'label': 'Select All', 'value': 'ALL'}] + [{'label': a, 'value': a} for a in sorted(df["Agency Name"].unique())],
        value=['ALL'],
        multi=True,
        clearable=False,
        maxHeight=600,
        optionHeight=50
    ),
], className="mb-4")

keyword_search = html.Div([
    dbc.Label("Search Table", html_for="keyword-search"),
    dbc.Input(
        id="keyword-search",
        type="text",
        placeholder="Enter keyword (e.g., 'Health', 'Education')",
        debounce=True,
        className="mb-4"
    ),
])

control_panel = dbc.Card(
    dbc.CardBody([
        county_dropdown,
        agency_dropdown,
        keyword_search,
        dbc.Button("Export Filtered Data", id="export-button", n_clicks=0, color="primary", className="mt-2"),
        dcc.Download(id="download-dataframe-csv")
    ]),
    className="mb-4 bg-light"
)

def make_grid():
    column_defs = [
        {"field": "County", "pinned": "left", "filter": "agTextColumnFilter"},
        {"field": "Agency Name", "filter": "agTextColumnFilter"},
        {"field": "Major Spending Category", "filter": "agTextColumnFilter"},
        {"field": "Amount", "filter": "agNumberColumnFilter", "valueFormatter": {"function": "d3.format('$,.2f')(params.value)"}},
        {"field": "Agency Number", "filter": "agTextColumnFilter"},
        {"field": "Fiscal Year", "filter": "agNumberColumnFilter"}
    ]
    column_defs = [col for col in column_defs if col["field"] in df.columns]
    return dag.AgGrid(
        id="grid",
        rowData=df.to_dict("records"),
        columnDefs=column_defs,
        defaultColDef={"filter": True, "floatingFilter": True, "wrapHeaderText": True, "autoHeaderHeight": True, "initialWidth": 150},
        dashGridOptions={"quickFilterText": ""},
        style={"height": 600, "width": "100%"}
    )

layout = html.Div([
    html.H1("Expenditure Table"),
    dbc.Row([
        dbc.Col(control_panel, md=3),
        dbc.Col([
            dcc.Markdown(id="title"),
            dbc.Row([dbc.Col(html.Div(id="expenditure-card"))]),
            html.Div(id="bar-chart-card", className="mt-4"),
        ], md=9)
    ]),
    dbc.Row(dbc.Col(make_grid()), className="my-4"),
    dcc.Store(id="store-selected", data={})
])

@callback(
    Output("grid", "rowData"),
    Output("store-selected", "data"),
    Input("county-dropdown", "value"),
    Input("agency-dropdown", "value"),
    Input("keyword-search", "value")
)
def update_grid(counties, agencies, keyword):
    dff = df.copy()
    if 'ALL' not in counties:
        dff = dff[dff["County"].isin(counties)]
    if 'ALL' not in agencies:
        dff = dff[dff["Agency Name"].isin(agencies)]
    if keyword:
        dff = dff[dff.apply(lambda row: row.astype(str).str.contains(keyword, case=False).any(), axis=1)]
    records = dff.to_dict("records")
    return records, records

@callback(
    Output("bar-chart-card", "children"),
    Input("store-selected", "data")
)
def make_bar_chart(data):
    if not data or not data[0]:
        fig = {}
    else:
        dff = pd.DataFrame(data)
        total_amount = dff["Amount"].sum()
        agency = dff["Agency Name"].iloc[0]
        county = dff["County"].iloc[0]
        fig = go.Figure([go.Bar(x=["Total Amount"], y=[total_amount], name=agency, text=f"${total_amount:,.2f}", textposition="auto")])
        fig.update_layout(
            title=f"Total Expenditure for {agency} in {county}",
            yaxis_title="Amount ($)",
            template="plotly_white"
        )
    return dbc.Card([dbc.CardHeader(html.H2("Expenditure Breakdown"), className="text-center"), dcc.Graph(figure=fig, style={"height": 250}, config={'displayModeBar': False})])

@callback(
    Output("title", "children"),
    Input("store-selected", "data")
)
def make_title(data):
    if not data or not data[0]:
        return "## Select Counties and Agencies"
    dff = pd.DataFrame(data)
    counties = dff["County"].unique()
    agencies = dff["Agency Name"].unique()
    fiscal_year = dff["Fiscal Year"].iloc[0]
    county_text = "Multiple Counties" if len(counties) > 1 else counties[0]
    agency_text = "Multiple Agencies" if len(agencies) > 1 else agencies[0]
    return f"## {fiscal_year} Expenditure Report for {agency_text} in {county_text}"

@callback(
    Output("expenditure-card", "children"),
    Input("store-selected", "data")
)
def make_expenditure_card(data):
    if not data or not data[0]:
        return ""
    dff = pd.DataFrame(data)
    total_amount = dff["Amount"].sum()
    sample_row = dff.iloc[0]
    major_spending_category = sample_row.get("Major Spending Category", "N/A")
    agency_number = sample_row.get("Agency Number", "N/A")
    return dbc.Card([
        dbc.CardHeader(html.H2("Expenditure Details"), className="text-center"),
        dbc.CardBody([
            html.Div(f"Total Amount: ${total_amount:,.2f}"),
            html.Div(f"Major Spending Category: {major_spending_category}"),
            html.Div(f"Agency Number: {agency_number}")
        ])
    ])

@callback(
    Output("download-dataframe-csv", "data"),
    Input("export-button", "n_clicks"),
    State("store-selected", "data"),
    prevent_initial_call=True
)
def export_filtered_data(n_clicks, filtered_data):
    if filtered_data:
        dff = pd.DataFrame(filtered_data)
        return dcc.send_data_frame(dff.to_csv, "texas_expenditure_filtered.csv", index=False)
    return dash.no_update