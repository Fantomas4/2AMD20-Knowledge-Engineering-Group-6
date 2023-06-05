import json

import pandas as pd
import plotly.express as px
from dash import html, dcc

from config import focused_attributes
from main import app
from views.menu import make_menu_layout
from dash.dependencies import Input, Output


def update_choropleth(target_df, focused_attribute, selected_establishment_sizes=None, aggregation='mean'):
    """
    Used to update the choropleth figure
    :param target_df: the dataframe containing the data that will be used by the choropleth figure
    :param focused_attribute: the attribute of target_df we want to visualize on the choropleth
    :param selected_establishment_sizes: list containing the selected establishment size strings
    :param aggregation: string that defines the aggregation we want to apply to our data within the choropleth
    :return: a figure object representing the generated choropleth figure
    """
    # Filter target_df based on the selected establishment sizes
    if selected_establishment_sizes is None:
        selected_establishment_sizes = []
    target_df = target_df[target_df['Business size'].isin(selected_establishment_sizes)]

    aggr_str_mapping = {'mean': 'Mean',
                        'min': 'Min.', 'max': 'Max.'}

    agg_attribute = aggr_str_mapping[aggregation] + ' ' + focused_attribute

    # Perform the selected aggregation on the dataframe
    target_df[agg_attribute] = target_df.groupby("State")[focused_attribute].transform(aggregation)

    fig = px.choropleth(data_frame=target_df,
                        locations="State code",
                        locationmode="USA-states",
                        hover_name="State",
                        scope="usa",
                        color=agg_attribute,
                        color_continuous_scale='greens',
                        )
    fig.update_layout(margin=dict(t=0, r=0, l=0, b=0))

    return fig


def update_histogram(target_df, focused_attribute, selected_data=None, selected_establishment_sizes=None):
    """
    Used to update the histogram figure
    :param target_df: the dataframe containing the data that will be used by PCP
    :param focused_attribute: the attribute of target_df we want to visualize on PCP
    :param selected_data: contains the data points selected using the "lasso" or "box selection" tool of the choropleth
    figure; None if no such selection is made
    :param selected_establishment_sizes: list containing the selected establishment size strings
    :return: a figure object representing the generated histogram figure
    """
    # Filter target_df based on the selected establishment sizes
    if selected_establishment_sizes is None:
        selected_establishment_sizes = []
    target_df = target_df[target_df['Business size'].isin(selected_establishment_sizes)]

    if selected_data:
        # If a data selection is provided, filter target_df accordingly
        states = [x['location'] for x in selected_data['points']]
        target_df = target_df[target_df['State code'].isin(states)]

    fig = px.histogram(target_df[focused_attribute])
    fig.update_xaxes(title="Value")
    fig.update_yaxes(title="Count")
    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="left",
    ))
    fig.update_layout(legend_title_text='Variable:', margin=dict(r=10, b=4, t=4, l=3))

    return fig


if __name__ == '__main__':
    # Read the data from the csv file
    cbp_df = pd.read_csv(
        "../datasets/generated/final_preprocessed.csv", low_memory=False)

    # Set the default focused attribute
    default_focused_attr = focused_attributes[0]

    # Initialize choropleth figure
    choropleth_fig = update_choropleth(cbp_df, default_focused_attr)

    # Initialize histogram figure
    histogram_fig = update_histogram(cbp_df, default_focused_attr)


    app.layout = html.Div(
        id="app-container",
        children=[
            # Left column
            html.Div(
                id="left-column",
                className="two columns",
                children=make_menu_layout()
            ),
            # Middle column / map and PCP
            html.Div(
                id="middle-column",
                className="seven columns",
                children=[
                    html.H5('Map overview'),
                    dcc.Loading(
                        id="loading-1",
                        type="default",
                        children=[html.Div(id="loading-output-choropleth"),
                                  dcc.Graph(id="choropleth-mapbox", figure=choropleth_fig)]
                    ),
                ]
            ),
            # Right column / histogram and heatmap
            html.Div(
                id="right-column",
                className="three columns",
                style={"padding": 0,
                       "background-color": 'rgba(0, 0, 255, 0.0)'},
                children=[
                    html.H5('Ordered Attribute Distribution', id='attribute-label'),
                    dcc.Loading(
                        id="loading-3",
                        type="default",
                        children=[html.Div(id="loading-output-histogram"),
                                  dcc.Graph(id='histogram', figure=histogram_fig)]
                    ),
                ]
            ),
        ]
    )


    @app.callback(
        Output("choropleth-mapbox", "figure"),
        Output("attribute-label", "children"),
        Output("loading-output-choropleth", "children"),
        Input("select-focused-attribute", "value"),
        Input("aggregation-dropdown", "value"),
        Input("establishment-size-checklist", "value"))
    def update_choropleth_view(focused_attribute, aggregate_func, selected_establishment_sizes):
        return update_choropleth(cbp_df, focused_attribute, selected_establishment_sizes=selected_establishment_sizes,
                                 aggregation=aggregate_func), \
               "Distribution of {}".format(focused_attribute), \
               None


    @app.callback(
        Output("histogram", "figure"),
        Output("loading-output-histogram", "children"),
        Input('choropleth-mapbox', 'selectedData'),
        Input("select-focused-attribute", "value"),
        Input("establishment-size-checklist", "value"))
    def update_histogram_view(selected_data, focused_attribute, selected_establishment_sizes):
        return update_histogram(cbp_df, focused_attribute, selected_data=selected_data,
                                selected_establishment_sizes=selected_establishment_sizes), None


app.run_server(debug=True, dev_tools_ui=True)
