import plotly.graph_objs as go
from django_plotly_dash import DjangoDash
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import (Input, Output)

external_scripts = ['https://www.google-analytics.com/analytics.js']
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = DjangoDash('MyApp')
app.layout = html.Div([
    html.Div([
        dcc.RadioItems(
            id='map-type',
            options=[{'label': s, 'value': s}
                     for s in ['Density Map', 'Scatter Map']],
            value='Density Map',
            labelStyle={'display': 'inline-block'}
        )
    ], style={'margin-left': 20, 'margin-top': 20, 'margin-bottom': 10}
    ),
    html.Div([dcc.Interval(id='output-update', interval=180*1000)]),
    html.Div(id='map-quakes'),
    html.Div([
        html.Div([
            html.Div(id='pie-quake-type')
        ], className='five columns'),
        html.Div([
            html.Div(id='area-count-plot')
        ], className='seven columns')
    ], className='row', style={'margin-left': 20, 'margin-top': 30}),
    html.Div([])
], style={'margin-top': 20, 'margin-bottom': 20})


def GrabOccurrenceData(past_occurrence, mag_value):
    url = 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/' + \
        str(past_occurrence) + '.csv'
    qdf = pd.read_csv(url)
    qdf = qdf[qdf['mag'] > int(mag_value)]
    return qdf


def GrabSpecificArea(past_occurrence, mag_value):
    qdf = GrabOccurrenceData(past_occurrence, mag_value)
    places = qdf['place'].to_list()
    specific_areas = []
    for place in places:
        area = place.split(', ')
        if len(area) == 2:
            specific_areas.append(area[1])
        if len(area) < 2:
            specific_areas.append(area[0])
    area_counts = []
    for area in specific_areas:
        area_counts.append(area+' - '+str(specific_areas.count(area)))
        specific_areas = list(set(area_counts))

    return specific_areas

# <DensityMap>


def PlotDensityMap(lat, lon, z, radius, colorscale):
    density_map_trace = go.Densitymapbox(
        lat=lat,
        lon=lon,
        z=z,
        radius=radius,
        colorscale=colorscale,
    )
    return density_map_trace


def LayoutDensity(height, width, mapbox_style, c_lat, c_lon, zoom):
    layout_density_map = go.Layout(
        height=height,
        width=width,
        autosize=True,
        showlegend=False,
        hovermode='closest',
        margin=dict(l=0, r=0, t=0, b=0),
        mapbox_style=mapbox_style,
        mapbox_center_lat=c_lat,
        mapbox_center_lon=c_lon,
        mapbox=dict(
            zoom=zoom
        )
    )
    return layout_density_map


def PlotScatterMap(lat, lon, size, color, colorscale, text):
    scatter_map_trace = go.Scattermapbox(
        lat=lat,
        lon=lon,
        mode='markers',
        marker=dict(
            size=size, color=color, opacity=1,
            colorscale=colorscale,
        ),
        text=text, hoverinfo='text', showlegend=True
    )
    return scatter_map_trace


def LayoutScatter(height, width, mapbox_style, c_lat, c_lon, zoom):
    layout_scatter_map = go.Layout(
        height=height,
        width=width,
        autosize=True,
        showlegend=False,
        hovermode='closest',
        margin=dict(l=0, r=0, t=0, b=0),
        mapbox_style=mapbox_style,
        mapbox=dict(
            center=dict(
                lat=c_lat,
                lon=c_lon
            ),
            zoom=zoom
        )
    )
    return layout_scatter_map


# <density_scatter_mapbox>
@app.callback(
    Output('map-quakes', 'children'),
    [Input('past-occurrence', 'value'), Input('magnitude-range', 'value'), Input('map-type', 'value'), Input('area-list', 'value'),
        Input('output-update', 'n_intervals')],
)
def visualize_quakes(past_occurrence, mag_value, map_type, specific_area, n_intervals):
    try:
        eqdf = GrabOccurrenceData(past_occurrence, mag_value)
        eqdf = eqdf[eqdf['place'].str.contains(
            str(specific_area.split(' - ')[0]))]
        zoom = 3
        radius = 15
        latitudes = eqdf['latitude'].to_list()
        longitudes = eqdf['longitude'].to_list()
        magnitudes = eqdf['mag'].to_list()
        mags = [float(i)*eqdf['outer'] for i in magnitudes]
        mags_info = ['Magnitude : ' + str(m) for m in magnitudes]
        depths = eqdf['depth'].to_list()
        deps_info = ['Depth : ' + str(d) for d in depths]
        places = eqdf['place'].to_list()
        center_lat = eqdf[eqdf['mag'] ==
                          eqdf['mag'].max()['latitude'].to_list()[0]]
        center_lon = eqdf[eqdf['mag'] == eqdf['mag'].max()]['longitude'].to_list()[
            0]
        if (map_type == 'Density Map'):
            map_trace = PlotDensityMap(
                latitudes, longitudes, magnitudes, radius, 'Electric')
            layout_map = LayoutDensity(
                600, 980, 'stamen-terrain', center_lat, center_lon, zoom)
            visualization = html.Div([
                dcc.Graph(
                    id='density-map',
                    figure={'data': [map_trace], 'layout': layout_map}
                ),
            ])
            return visualization
        if (map_type == 'Scatter Map'):
            quake_info = [places[i] + '<br>' + mags_info[i] +
                          '<br>' + deps_info[i] for i in range(eqdf.shape[0])]
            map_trace = PlotScatterMap(
                latitudes, longitudes, mags, magnitudes, default_colorscale, quake_info)
            layout_map = LayoutScatter(
                600, 980, 'stamen-terrain', center_lat, center_lon, zoom)
            visualization = html.Div([
                dcc.Graph(
                    id='scatter-map',
                    figure={'data': [map_trace], 'layout': layout_map}
                ),
            ])
            return visualization
    except Exception as e:
        return html.Div([
            html.H6('Please select valid magnitude / region ...')
        ], style={'margin-top': 150, 'margin-bottom': 150, 'margin-left': 200})
    # </density_scatter_mapbox>
