import os
import pathlib
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
gdf = gpd.read_file(geojson_file)
gdf_cols = gdf.columns

# ------
# Create url column with missing values
gdf['url_original'] = gdf['url']
gdf['HUC8'] = gdf['HUC8'].apply(pd.to_numeric, errors='ignore')
gdf['url'] = gdf.apply(lambda row: row.url if row.HUC8 % 2 == 0 else '' , axis=1)
gdf['available'] = gdf.apply(lambda row: 0 if row.url == '' else 1 , axis=1)

map_gdf = gdf[~(gdf.url == '')]
# ------


map_center_lat = gdf.centroid.y.mean()
map_center_lon = gdf.centroid.x.mean()

## Always make sure data is already in EPSG:4326
#gdf = gdf.to_crs(epsg=4326)

# ----------------------------------------------------------------------------
# Figure Generation
# ----------------------------------------------------------------------------

#fig = px.scatter(df, x="x", y="y", color="fruit", custom_data=["customdata"])
fig = px.choropleth_mapbox(
    gdf,
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
    clickmode = 'event+select',
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
                figure=fig
            ),
        ],width=4),
        dbc.Col([
            html.H4('Selected HUC8s '),
            html.Div(id='map-selected'),
            # dcc.ConfirmDialog(
            #     id='confirm',
            #     message='Danger danger! Are you sure you want to continue?',
            # ),
            html.Button(
                'Download',
                id = 'btn_download',
            ),
            ],width=4),
        dbc.Col([html.H4('Downloaded HUC8s'),html.P('refresh your browser to clear this list.')],width=4),
    ]),

    dbc.Row(
        dbc.Col([


        ])
    ),

    dbc.Row([
        dbc.Col([html.P(col) for col in gdf_cols],width=6),
        dbc.Col([html.P('b')],width=6),
    ])

])

# ----------------------------------------------------------------------------
# CALLBACKS
# ----------------------------------------------------------------------------


@app.callback(
    Output('map-selected', 'children'),
    Input('graph-map', 'selectedData'))
def display_selected_data(selectedData):
    data = json.dumps(selectedData)
    return data


if __name__ == '__main__':
    app.run_server(debug=True)
else:
    server = app.server
