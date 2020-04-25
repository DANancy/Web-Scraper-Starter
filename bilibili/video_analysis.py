#! /usr/bin/env python3
# -*- coding: utf-8 -*-

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

# others
from datetime import datetime


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
        return data
    dff = data[data.author == name]
    return dff


data = fetch_data('bilibili', 'infos')
author_by_video = data['author'].value_counts().to_frame('y')[:10]
opts = [{'label': i, 'value': i} for i in data.author.unique()]
unique_dates = data['pubdate_new'].unique()
dates = sorted([str(unique_dates[i]) for i in range(0, len(unique_dates))])
date_mark = {i: dates[i] for i in range(0, len(unique_dates))}

#########################
# Dashboard Layout / View
#########################

app = dash.Dash()

colors = {
    'background': '#FFFFFF',
    'text': 'black'
}

trace_1 = pgo.Scatter(x=author_by_video.index, y=author_by_video['y'],
                      name='Videos by time',
                      line=dict(width=2,
                                color='rgb(229, 151, 50)'))
layout = pgo.Layout(title='Time Series Plot',
                    hovermode='closest')
fig = pgo.Figure(data=[trace_1], layout=layout)

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    # add a header
    html.H1(
        children='Bilibili Data Visualization',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),
    # add a paragraph
    html.Div(children='Bilibili videos data visualization using Dash.', style={
        'textAlign': 'center',
        'color': colors['text']
    }),

    # add a bar plot
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

    # adding a plot
    dcc.Graph(
        id='plot', figure=fig),

    # add dropdown
    html.P([
        html.Label("Choose a name"),
        dcc.Dropdown(id='dropdown', options=[
            {'label': i, 'value': i} for i in data.author.unique()
        ], multi=False, placeholder='Filter by Author...'),
    ], style={'width': '400px', 'fontSize': '20px', 'padding-left': '100px', 'display': 'inline-block'}),

    # add range slider
    html.P([
        html.Label("Time Period"),
        dcc.RangeSlider(id='slider',
                        marks=date_mark,
                        min=0,
                        max=8,
                        value=[0, 6])], style={'width': '80%',
                                               'fontSize': '20px',
                                               'padding-left': '100px',
                                               'display': 'inline-block'})

])


#############################################
# Interaction Between Components / Controller
#############################################
@app.callback(
    Output('plot', 'figure'),
    [Input('dropdown', 'value'),
     Input('slider', 'value')])
def update_figure(input1, input2):
    # filtering the data
    st1 = generate_data(input1)
    from_date = datetime.strptime(dates[input2[0]], '%Y-%m-%d').date()
    to_date = datetime.strptime(dates[input2[1]], '%Y-%m-%d').date()
    st2 = st1[(st1.pubdate_new > from_date) & (st1.pubdate_new < to_date)]
    updated_data = st2['pubdate_new'].value_counts().sort_index().to_frame('y')

    # update the plot
    trace_1 = pgo.Scatter(x=updated_data.index, y=updated_data['y'],
                          name='Videos by Date',
                          line=dict(width=2,
                                    color='rgb(229, 151, 50)'))
    fig = pgo.Figure(data=[trace_1], layout=layout)
    return fig


# start Flask server
if __name__ == "__main__":
    app.run_server(debug=True)
