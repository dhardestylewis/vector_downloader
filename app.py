import json

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px
#import pandas as pd
import geopandas as gpd


#gdf = gpd.read_file('https://gist.githubusercontent.com/Tlaloc-Es/5c82834e5e4a9019a91123cb11f598c0/raw/709ce9126861ef7a7c7cc4afd6216a6750d4bbe1/mexico.geojson')
gdf = gpd.read_file('data/fathom3m_coverage_tacc.geojson')
gdf = gdf.to_crs(epsg=4326)


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

#df = pd.DataFrame({
#    "x": [1,2,1,2],
#    "y": [1,2,3,4],
#    "customdata": [1,2,3,4],
#    "fruit": ["apple", "apple", "orange", "orange"]
#})

#fig = px.scatter(df, x="x", y="y", color="fruit", custom_data=["customdata"])
fig = px.choropleth_mapbox(
    gdf,
    geojson = gdf.geometry,
    locations = gdf.index,
    color = 'AREA',
    color_continuous_scale = "Viridis",
    range_color = (0,12),
    mapbox_style = "open-street-map",
    zoom = 3,
    center = {
        "lat" : gdf.centroid.y.mean(),
        "lon" : gdf.centroid.x.mean()
    },
    opacity = 0.5
)

fig.update_layout(
    margin = {
        "r" : 0,
        "t" : 0,
        "l" : 0,
        "b" : 0
    },
    clickmode = 'event+select',
    height = 700
)

#fig.update_traces(marker_size=20)

app.layout = html.Div([

    dcc.Graph(
        id='basic-interactions',
        figure=fig
    ),

    html.Div(className='row', children=[

        dbc.Row(
            dbc.Col([
                html.Button(
                    'Download',
                    id = 'btn_download',
                ),
                dcc.Download(id='download-files')
            ])
        ),

        dbc.Row([

            html.Div([
                dcc.Markdown("""
                    **Hover Data**
    
                    Mouse over values in the graph.
                """),
                html.Pre(id='hover-data', style=styles['pre'])
            ], className='three columns'),
    
            html.Div([
                dcc.Markdown("""
                    **Click Data**
    
                    Click on points in the graph.
                """),
                html.Pre(id='click-data', style=styles['pre']),
            ], className='three columns'),
    
            html.Div([
                dcc.Markdown("""
                    **Selection Data**
    
                    Choose the lasso or rectangle tool in the graph's menu
                    bar and then select points in the graph.
    
                    Note that if `layout.clickmode = 'event+select'`, selection data also
                    accumulates (or un-accumulates) selected data if you hold down the shift
                    button while clicking.
                """),
                html.Pre(id='selected-data', style=styles['pre']),
            ], className='three columns'),
    
            html.Div([
                dcc.Markdown("""
                    **Zoom and Relayout Data**
    
                    Click and drag on the graph to zoom or click on the zoom
                    buttons in the graph's menu bar.
                    Clicking on legend items will also fire
                    this event.
                """),
                html.Pre(id='relayout-data', style=styles['pre']),
            ], className='three columns')

        ])

    ])
])


@app.callback(
    Output('intermediate-data', 'data'),
    [
        Input("btn_submit", "n_clicks"),
        Input('basic-interactions', 'selectedData')
    ]
)
def download(n_clicks,selectedData):
    triggered = dash.callback_context.triggered[0]['prop_id'].replace('.n_clicks','')
    if triggered == "btn_submit":
        download_data = gpd.GeoDataFrame(json.dumps(selectedData))
        urls = download_data.iloc[download_data.index]['url'].to_list()
        return(urls)



@app.callback(
    Input("intermediate-data", 'urls'),
    prevent_initial_call = True
)
def make_download(urls):
    for url in urls:
        dcc.Download(id=url)


@app.callback(
    Output('hover-data', 'children'),
    Input('basic-interactions', 'hoverData'))
def display_hover_data(hoverData):
    return json.dumps(hoverData, indent=2)


@app.callback(
    Output('click-data', 'children'),
    Input('basic-interactions', 'clickData'))
def display_click_data(clickData):
    return json.dumps(clickData, indent=2)


@app.callback(
    Output('selected-data', 'children'),
    Input('basic-interactions', 'selectedData'))
def display_selected_data(selectedData):
    return json.dumps(selectedData, indent=2)


@app.callback(
    Output('relayout-data', 'children'),
    Input('basic-interactions', 'relayoutData'))
def display_relayout_data(relayoutData):
    return json.dumps(relayoutData, indent=2)


if __name__ == '__main__':
    app.run_server(debug=True)
else:
    server = app.server

