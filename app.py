import json

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
import plotly.express as px
#import pandas as pd
import geopandas as gpd
import pandas as pd
import ast


#gdf = gpd.read_file('https://gist.githubusercontent.com/Tlaloc-Es/5c82834e5e4a9019a91123cb11f598c0/raw/709ce9126861ef7a7c7cc4afd6216a6750d4bbe1/mexico.geojson')
## refer to data/fim3outputs_coverage_simplified.geojson.py for preprocessing
gdf = gpd.read_file('data/fim3outputs_coverage_simplified.geojson')

## Always make sure data is already in EPSG:4326
#gdf = gdf.to_crs(epsg=4326)


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
                html.Pre(id='url_list'),
                dcc.Store(id='btn_download_triggered'),
                html.Pre(id='button_triggered_value'),
                html.Pre(id='downloading_now_value'),
                html.Pre(id='list_populated_value'),
                dcc.Store(id='url_list_evaled'),
                dcc.Store(id='urls_left_to_download'),
                dcc.Store(id='url_list_populated'),
                dcc.Store(id='downloading_one_at_a_time'),
                dcc.Store(id='just_one_url'),
                dcc.Store(id='url_list_completed'),
                html.Div(id='urls_downloading', children=[]),
                html.Div(id='popped_urls', children=[]),
                html.Div(id='url_downloading'),
                html.Div(id='popped_url')
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


#@app.callback(
#    Output('intermediate-data', 'data'),
#    [
#        Input("btn_download", "n_clicks"),
#        Input('basic-interactions', 'selectedData')
#    ]
#)
#def download(n_clicks,selectedData):
#    triggered = dash.callback_context.triggered[0]['prop_id'].replace('.n_clicks','')
#    if triggered == "btn_submit":
#        download_data = gpd.GeoDataFrame(json.dumps(selectedData))
#        urls = download_data.iloc[download_data.index]['url'].to_list()
#        return(urls)
#
#
#@app.callback(
#    Input("intermediate-data", 'data'),
#    prevent_initial_call = True
#)
#def make_download(urls):
#    for url in urls:
#        dcc.Download(id=url)


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
    [
        Output('selected-data', 'children'),
        Output('url_list', 'children')
    ],
    Input('basic-interactions', 'selectedData'))
def display_selected_data(selectedData):
#    data = json.dumps(selectedData)
#    download_data = gpd.GeoDataFrame(data)
#    urls = download_data.iloc[download_data.index]['url'].to_list()
    if selectedData is not None:
        url_list = pd.DataFrame(
            selectedData['points']
        )['pointIndex'].to_list()
        url_list = gdf.iloc[url_list]['url'].to_list()
    else:
        url_list = 'None'
    return json.dumps(selectedData, indent=2),str(url_list)
#    return ','.join(urls)


@app.callback(
    Output('btn_download_triggered', 'data'),
    Input('btn_download', 'n_clicks')
)
def begin_download(
    n_add : int
):
    triggered = dash.callback_context.triggered[0]['prop_id']
    if triggered == 'btn_download.n_clicks':
        ## TODO: reset callback_context above
        return True
    else:
        return False
    return False


@app.callback(
    Output('downloading_one_at_a_time', 'data'),
    Input('urls_left_to_download', 'data')
)
def still_downloading(urls_downloading):

    if urls_downloading is None:
        urls_downloading = []

    if len(urls_downloading) > 0:
        return(True)
    else:
        return(False)

    return(False)


@app.callback(
    Output('downloading_now_value', 'children'),
    Input('downloading_one_at_a_time', 'data')
)
def print_button_status(btn_download_triggered):
    return([str(btn_download_triggered)])


@app.callback(
    Output('button_triggered_value', 'children'),
    Input('btn_download_triggered', 'data')
)
def print_button_status(btn_download_triggered):
    return([str(btn_download_triggered)])


@app.callback(
    Output('list_populated_value', 'children'),
    Input('url_list_populated', 'data')
)
def print_button_status(btn_download_triggered):
    return([str(btn_download_triggered)])


@app.callback(
    Output('url_list_evaled', 'data'),
    [
        Input('btn_download_triggered', 'data'),
        Input('url_list', 'children')
    ]
)
def prepare_download(btn_download_triggered,url_list):
    if btn_download_triggered and url_list is not None:
        download_urls = []
        for url in ast.literal_eval(url_list):
            download_urls.append(url)
#            element = html.Div(html.A("Test", href=url,target='_blank'))
        return(download_urls)


@app.callback(
    [
        Output('popped_urls', 'children'),
        Output('popped_url', 'children'),
        Output('url_list_completed', 'data')
    ],
    [
        Input('url_list_populated', 'data'),
        Input('urls_downloading', 'children'),
    ],
    State('popped_urls', 'children')
)
def download_urls(url_list_populated, url_to_download, popped_urls):
    if not url_list_populated:
        url_list_completed = False
        popped_url = 'No current download'
    else:
        triggered = dash.callback_context.triggered[0]['prop_id'].replace(
            'btn_download.n_clicks',
            ''
        )
        if url_to_download is not None:
            popped_url = popped_urls.pop()
            url_list_completed = False
            return(popped_urls,popped_url,url_list_completed)
        else:
            url_list_completed = True
            return(popped_urls,popped_url,url_list_completed)
    return(popped_urls,popped_url,url_list_completed)


@app.callback(
    Output('url_downloading', 'children'),
    [
        Input({
            'type' : 'download_triggered',
            'index' : ALL
        }, 'value'),
        Input('urls_downloading', 'children')
    ]
)
def trigger_download(ignore,values):
    if values is not None:
        return(html.Div([
            html.Div(value)
            for value in values
        ]))


@app.callback(
    [
        Output('urls_downloading', 'children'),
        Output('url_list_populated', 'data')
    ],
    [
        Input('btn_download_triggered', 'data'),
        Input('url_list_evaled', 'data'),
    ],
    State('urls_downloading', 'children')
)
def download_urls(btn_download_triggered, url_list_evaled, urls_to_download):
    if not btn_download_triggered:
        url_list_populated = False
    else:
        if url_list_evaled is not None:
            for url_to_download in url_list_evaled:
                url_element_to_download = dcc.Location(
                    id = {
                        'type' : 'download_triggered',
                        'index' : url_to_download,
                    },
                    href = url_to_download,
                    refresh = True
                )
                urls_to_download.append(url_element_to_download)
            url_list_populated = False
            return(urls_to_download,url_list_populated)
        else:
            url_list_populated = True
            return(urls_to_download,url_list_populated)
    return(urls_to_download,url_list_populated)


#@app.callback(
#    Output('url_downloading', 'children'),
#    [
#        Input({
#            'type' : 'download_triggered',
#            'index' : ALL
#        }, 'value'),
#        Input('urls_downloading', 'children')
#    ]
#)
#def trigger_download(ignore,values):
#    if values is not None:
#        return(html.Div([
#            html.Div(value)
#            for value in values
#        ]))


@app.callback(
    Output('relayout-data', 'children'),
    Input('basic-interactions', 'relayoutData'))
def display_relayout_data(relayoutData):
    return json.dumps(relayoutData, indent=2)


if __name__ == '__main__':
    app.run_server(debug=True)
else:
    server = app.server

