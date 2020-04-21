# env libs
import os
from dotenv import load_dotenv
from pathlib import Path

# dash libs
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as pgo

# pydata stack
import pandas as pd
import pymongo

# set params
env_path = Path('..') / '.env'
load_dotenv(dotenv_path=env_path)
myClient = pymongo.MongoClient(os.getenv("DBCONNECT"))


###########################
# Data Manipulation / Model
###########################
def fetch_data(db, table):
    df = pd.DataFrame(list(myClient[db][table].find()))
    df['pubdate_new'] = pd.to_datetime(df['pubdate']).dt.date
    return df


def generate_data(name):
    data = fetch_data('bilibili', 'infos')
    if name is None:
        return data['pubdate_new'].value_counts().sort_index().to_frame('y')
    dff = data[data.author == name]
    return dff['pubdate_new'].value_counts().sort_index().to_frame('y')


data = fetch_data('bilibili', 'infos')
author_by_video = data['author'].value_counts().to_frame('y')[:10]
video_by_date = data['pubdate_new'].value_counts().sort_index().to_frame(
    'y')
opts = [{'label': i, 'value': i} for i in data.author.unique()]

#########################
# Dashboard Layout / View
#########################
app = dash.Dash()

colors = {
    'background': '#FFFFFF',
    'text': 'black'
}

trace_1 = pgo.Scatter(x=video_by_date.index, y=video_by_date['y'],
                      name='Videos by time',
                      line=dict(width=2,
                                color='rgb(229, 151, 50)'))
layout = pgo.Layout(title='Time Series Plot',
                    hovermode='closest')
fig = pgo.Figure(data=[trace_1], layout=layout)

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(
        children='Bilibili Data Visualization',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    html.Div(children='Bilibili videos data visualization using Dash.', style={
        'textAlign': 'center',
        'color': colors['text']
    }),

    dcc.Graph(
        id='top-authors-by-videos',
        figure={
            'data': [
                {'x': author_by_video.index,
                 'y': author_by_video['y'],
                 'type': 'bar'}
            ],
            'layout': {
                'title': 'Top 10 Auhtors by Videos',
                'plot_bgcolor': colors['background'],
                'paper_bgcolor': colors['background'],
                'font': {
                    'color': colors['text']
                }
            }
        }
    ),

    dcc.Graph(
        id='plot', figure=fig),

    html.P([
        html.Label("Choose a name"),
        dcc.Dropdown(id='dropdown', options=[
            {'label': i, 'value': i} for i in data.author.unique()
        ], multi=False, placeholder='Filter by Author...'),
    ], style={'width': '400px', 'fontSize': '20px', 'padding-left': '100px', 'display': 'inline-block'})
])


#############################################
# Interaction Between Components / Controller
#############################################

@app.callback(
    Output('plot', 'figure'),
    [Input('dropdown', 'value')])
def update_figure(dropdown_value):
    updated_data = generate_data(dropdown_value)
    trace_1 = pgo.Scatter(x=updated_data.index, y=updated_data['y'],
                          name='Videos by time',
                          line=dict(width=2,
                                    color='rgb(229, 151, 50)'))
    layout = pgo.Layout(title='Time Series Plot',
                        hovermode='closest')
    fig = pgo.Figure(data=[trace_1], layout=layout)

    return fig


# start Flask server
if __name__ == "__main__":
    app.run_server(debug=True)
