import os
import io
import pathlib
import json
import requests
import base64

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
from dash.exceptions import PreventUpdate
from dash_extensions import Download
from dash_extensions.snippets import send_file
import dash_table as dt


import plotly.express as px
#import pandas as pd
import geopandas as gpd
import pandas as pd
import ast

# ----------------------------------------------------------------------------
# Styles (**MOVE THIS TO SEPERATE FILE / CSS)
# ----------------------------------------------------------------------------

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}


# ----------------------------------------------------------------------------
# DATA LOADING
# ----------------------------------------------------------------------------

#gdf = gpd.read_file('https://gist.githubusercontent.com/Tlaloc-Es/5c82834e5e4a9019a91123cb11f598c0/raw/709ce9126861ef7a7c7cc4afd6216a6750d4bbe1/mexico.geojson')
## refer to data/fim3outputs_coverage_simplified.geojson.py for preprocessing
data_filepath = pathlib.Path(__file__).parent.absolute()
geojson_file = os.path.join(data_filepath,'data','fim3outputs_coverage_simplified.geojson')
gdf_og = gpd.read_file(geojson_file)
gdf_cols = gdf_og.columns

# ------
# Create url column with missing values
gdf_og['url_original'] = gdf_og['url']
gdf_og['HUC8'] = gdf_og['HUC8'].apply(pd.to_numeric, errors='ignore')
gdf_og['url'] = gdf_og.apply(lambda row: row.url if row.HUC8 % 2 == 0 else '' , axis=1)
gdf_og['available'] = gdf_og.apply(lambda row: 0 if row.url == '' else 1 , axis=1)

gdf = gdf_og
map_gdf = gdf[~(gdf.url == '')].reset_index(drop=True)
# ------


map_center_lat = gdf.centroid.y.mean()
map_center_lon = gdf.centroid.x.mean()

## Always make sure data is already in EPSG:4326
#gdf = gdf.to_crs(epsg=4326)

# ----------------------------------------------------------------------------
# DATA DOWNLOADIND
# ----------------------------------------------------------------------------

example_image_prefix = 'https://raw.githubusercontent.com/dhardestylewis/vector_downloader/lissa_app/data/images/austin_'
example_image_suffix = '.png'
example_image_list = [2,3,4]

example_image_urls = []
for i in example_image_list:
    example_image_urls.append(''.join([example_image_prefix,str(i),example_image_suffix]))

#------------------------------
# Figure Generation
# ----------------------------------------------------------------------------

#fig = px.scatter(df, x="x", y="y", color="fruit", custom_data=["customdata"])
fig = px.choropleth_mapbox(
    map_gdf,
    geojson = map_gdf.geometry,
    locations = map_gdf.index,
    custom_data = [map_gdf['NAME'], map_gdf['HUC8']],
    # color_continuous_scale = "Viridis",
    # range_color = (0,12),
    mapbox_style = "open-street-map",
    zoom = 4,
    center = {
        "lat" : map_center_lat,
        "lon" : map_center_lon
    },
    opacity = 0.5,
)

fig.update_layout(
    margin = {
        "r" : 0,
        "t" : 0,
        "l" : 0,
        "b" : 0
    },
    clickmode = 'event+select', # 'event+select',
    height = 700,
    showlegend=False
)

fig.update_traces(
    hovertemplate="<br>".join([
        "%{customdata[0]}",
        "HUC8: %{customdata[1]}"
    ])
)

# ----------------------------------------------------------------------------
# APP Layout
# ----------------------------------------------------------------------------

external_stylesheets = [dbc.themes.LITERA]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


#fig.update_traces(marker_size=20)

app.layout = html.Div([
    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id='graph-map',
                figure=fig,

            ),
        ],width=4
        ,
        ),
        dbc.Col([
            html.H4('Selected HUC8s '),
            html.Div(id='map-selected'),
            dcc.ConfirmDialog(
                id='confirm',
            ),

            html.Button('Download files',
                id = 'btn_download',
                style={"margin":"20px"}
            ),

            html.Div(id='confirm-output'),
            dcc.Download(id="download-image")
            ],width=4
            ,
            ),
        dbc.Col([html.H4('Downloaded HUC8s'),
                html.P('refresh your browser to clear this list.'),
                html.Button('Download Test',
                    id = 'btn_test',
                    style={"margin":"20px"}
                ),
                dcc.Download(id="download-test"),
                html.Div(id='div_test'),
                ],width=4),
    ]),

    dbc.Row(
        dbc.Col([
            html.Div(id='download-output')

        ])
    ),

    dbc.Row([
        dbc.Col(id='bottom-left',width=6),
        dbc.Col(id = 'bottom-right',width=6),
    ])

])

# ----------------------------------------------------------------------------
# CALLBACKS
# ----------------------------------------------------------------------------

@app.callback(Output('div_test', 'children'),Output('download-test','data'),
                Input('btn_test', 'n_clicks'))
def display_test(n_clicks):
    triggered = dash.callback_context.triggered[0]['prop_id']
    if triggered == 'btn_test.n_clicks':
        image_url = ''.join([example_image_prefix,str(2),example_image_suffix])
        image_filename = image_url.split("/")[-1]
        image_content = requests.get(image_url).content
        content = base64.b64encode(image_content).decode()
        return 'download clicked', dict(filename=image_filename, content=content,  base64=True)

    return 'different button', None

@app.callback(
    Output('btn_download', 'disabled'),Output('map-selected', 'children'),
    Input('graph-map', 'selectedData'))
def display_selected_data(selectedData):
    if selectedData:
        button_status = False
        # children = json.dumps(selectedData)
        hucs_indices = pd.DataFrame(selectedData['points'])['pointIndex'].to_list()
        # gdf_selected = map_gdf.iloc[hucs_indices][['NAME','STATES','HUC8','url']]
        # children = dt.DataTable(
        #             id='table',
        #             columns=[{"name": i, "id": i} for i in gdf_selected.columns],
        #             data=gdf_selected.to_dict('records'),
        #             )

        children = []
        for i in hucs_indices:
            row_values = map_gdf.iloc[i]
            NAME = row_values['NAME']
            STATES = row_values['STATES']
            HUC8 = row_values['HUC8']
            if row_values['url']:
                url = row_values['url']
            else:
                url = 'empty?'
            children.append(html.Div([
                html.P([NAME, ' [',STATES,'], ', HUC8],style={'margin-bottom':0,'font-weight':'bold'}),
                html.P([url])
                ]))

    else:
        button_status = True
        children = html.Div([html.P('Please use the selection tools in the map to select one or more HUC8s for file download. '),html.Br()])
    return button_status, children


@app.callback(Output('confirm', 'displayed'),
                Output('confirm', 'message'),
                Input('btn_download', 'n_clicks'))
def display_confirm(n_clicks):
    triggered = dash.callback_context.triggered[0]['prop_id']
    if triggered == 'btn_download.n_clicks':
        return True, 'Note: the linked TIF files are large. Do you wish to continue?'
    return False, None


@app.callback(Output('confirm-output', 'children'),
              Input('confirm', 'submit_n_clicks'))
def update_output(submit_n_clicks):
    if submit_n_clicks:
        # Change this to show which files were downloaded
        return 'Notification of download'

@app.callback(
    Output("download-output", "children"),
    Output("download-image","data"),
    Input("btn_download", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    triggered = dash.callback_context.triggered[0]['prop_id']
    if n_clicks == 0:
        raise PreventUpdate
    if triggered == 'btn_download.n_clicks':
        msg = 'Triggered' + str(n_clicks)
        return msg, None



if __name__ == '__main__':
    app.run_server(debug=True)
else:
    server = app.server
