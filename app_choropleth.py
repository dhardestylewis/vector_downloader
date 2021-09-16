import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px

import geopandas as gpd

print('Loading data...')
gdf = gpd.read_file('https://gist.githubusercontent.com/Tlaloc-Es/5c82834e5e4a9019a91123cb11f598c0/raw/709ce9126861ef7a7c7cc4afd6216a6750d4bbe1/mexico.geojson')
gdf = gdf.to_crs(epsg=4326)

print('Done!')
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.Div([
                dcc.RadioItems(
                    id='radio-color_on',
                    options=[{'label': i, 'value': i} for i in ['AREA','PERIMETER']],
                    value='AREA',
                    labelStyle={'display': 'inline-block'}
                ),
    ],style={'width': '40%', 'display': 'inline-block',}),

html.Div([], style={'width':'100%'}),

    html.Div([
                dcc.Graph(id="fig")
    ],style={'width': '60%', 'display': 'inline-block', 'padding': '0 10',},),
]) 

@app.callback(
    Output("fig", "figure"), 
    [Input("radio-color_on", "value")])
def draw_choropleth(color_on):
    fig = px.choropleth_mapbox(gdf, 
                            geojson=gdf.geometry, 
                            locations=gdf.index, 
                            color=color_on,
                            color_continuous_scale="Viridis",
                            range_color=(0, 12),
                            mapbox_style="open-street-map",
                            zoom=3, 
                            center = {"lat":gdf.centroid.y.mean(), "lon":gdf.centroid.x.mean()},
                            opacity=0.5
                            )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0},
                        clickmode='event+select',
                        height=700,
                        )
    #fig.update_geos(fitbounds="locations", visible=False)
    return fig

@app.callback(
    Output(component_id='graphs', component_property='children'),
    [Input('map-flex', 'clickData')]
)
def display_click_data(custom_data):
    print(custom_data)

if __name__ == '__main__':
    app.run_server(debug=True,port=8030)
else:
    server = app.server

