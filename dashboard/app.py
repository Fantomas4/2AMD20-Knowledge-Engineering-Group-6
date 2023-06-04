import json

import pandas as pd
import plotly.express as px
from dash import html, dcc

from config import cat_attr_list, focused_attributes
from main import app
from views.menu import make_menu_layout, default_pcp_selections
from dash.dependencies import Input, Output, State


def update_choropleth(target_df, focused_attribute, selected_establishment_sizes=None, aggregation='mean'):
    """
    Used to update the choropleth figure
    :param target_df: the dataframe containing the data that will be used by the choropleth figure
    :param focused_attribute: the attribute of target_df we want to visualize on the choropleth
    :param geojson_data: dataset containing the geolocation information of NYC districts
    :param aggregate_func: defines the aggregate function selected by the user
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


def update_pcp(target_df, focused_attribute, selected_dimensions, selected_data=None,
               selected_establishment_sizes=None):
    """
    Used to update the PCP figure
    :param target_df: the dataframe containing the data that will be used by PCP
    :param selected_data: contains the data points selected using the "lasso" or "box selection" tool of the choropleth
    figure; None if no such selection is made
    :param focused_attribute: the attribute of target_df we want to visualize on PCP
    :param selected_dimensions: the selected attributes that should be put on PCP's axes
    :return: a figure object representing the generated PCP figure
    """
    # Filter target_df based on the selected establishment sizes
    if selected_establishment_sizes is None:
        selected_establishment_sizes = []
    target_df = target_df[target_df['Business size'].isin(selected_establishment_sizes)]

    if selected_data:
        # If a data selection is provided, filter target_df accordingly
        states = [x['location'] for x in selected_data['points']]
        target_df = target_df[target_df['State code'].isin(states)]

    fig = px.parallel_coordinates(data_frame=target_df,
                                  color=focused_attribute,
                                  dimensions=selected_dimensions,
                                  color_continuous_scale=px.colors.sequential.Blackbody,
                                  color_continuous_midpoint=2,
                                  range_color=[target_df[focused_attribute].min(), target_df[focused_attribute].max()])
    fig.update_layout(margin=dict(t=45, l=48, r=5, b=40))

    return fig


def update_histogram(target_df, focused_attribute, selected_data=None, selected_establishment_sizes=None):
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


def update_heatmap(target_df, focused_attribute, x_choice=cat_attr_list[0], y_choice=cat_attr_list[1],
                   aggregate_value='mean', selected_data=None, selected_establishment_sizes=None):
    """
    Used to update the heatmap figure
    :param target_df: the dataframe containing the data that will be used by the choropleth figure
    :param selected_data: contains the data points selected using the "lasso" or "box selection" tool of the choropleth
    figure; None if no such selection is made
    :param focused_attribute: the (quantitative) attribute of target_df we want to visualize on the heatmap using the colourmap
    :param x_choice: the selected (categorical) attribute that will be visualized on the heatmap's X axis
    :param y_choice: the selected (categorical) attribute that will be visualized on the heatmap's Y axis
    :param aggregate_value: the selected aggregate function name that will be applied to the heatmap's data
    :return:
    """
    # Filter target_df based on the selected establishment sizes
    if selected_establishment_sizes is None:
        selected_establishment_sizes = []
    target_df = target_df[target_df['Business size'].isin(selected_establishment_sizes)]

    # Convert aggregate_value to the appropriate format for the "histfunc" parameter of "density_heatmap()"
    if aggregate_value == "mean":
        aggregate_value = "avg"

    # If a data selection is provided, filter target_df accordingly
    if selected_data:
        states = [x['location'] for x in selected_data['points']]
        target_df = cbp_df[cbp_df['State code'].isin(states)]

    # If target_df is empty (due to filtering), create a dummy target_df that can be processed by density_heatmap()
    if target_df.empty:
        # column names are same as in original target_df
        target_df = pd.DataFrame({"#Establishments": [0],
                                  "Average annual payroll": [0],
                                  "Average first-quarter payroll": [0],
                                  "Average #employees": [0],
                                  "Men to women degree holders ratio": [0],
                                  "#(Mid)Senior degree holders": [0],
                                  "Degree holders to establishments ratio": [0],
                                  "Rate establishments born": [0],
                                  "Rate establishments exited": [0],
                                  "Rate born - exited": [0],
                                  "Min rank": [0],
                                  "Average rank": [0],
                                  "Max rank": [0],
                                  'Business size': [0],
                                  'Region': [0],
                                  '2nd Most popular degree field': [0],
                                  'State with top universities': [0]})

    heatmap_fig = px.density_heatmap(
        data_frame=target_df,
        x=target_df[x_choice],
        y=target_df[y_choice],
        z=target_df[focused_attribute],
        histfunc=aggregate_value
    )
    heatmap_fig.update_xaxes(dtick=1, fixedrange=True)
    heatmap_fig.update_yaxes(fixedrange=True)
    heatmap_fig.update_layout(margin=dict(r=2, b=4, t=10, l=3))

    return heatmap_fig


if __name__ == '__main__':
    # Read the data from the csv file
    cbp_df = pd.read_csv(
        "../datasets/CBP_preprocessed.csv", low_memory=False)

    # Set the default focused attribute
    default_focused_attr = focused_attributes[0]

    # Initialize choropleth figure
    choropleth_fig = update_choropleth(cbp_df, default_focused_attr)

    # Initialize histogram figure
    histogram_fig = update_histogram(cbp_df, default_focused_attr)

    # Initialize PCP figure
    pcp_fig = update_pcp(cbp_df, default_focused_attr, default_pcp_selections)

    # # Initialize heatmap figure
    heatmap_fig = update_heatmap(cbp_df, default_focused_attr)

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
                    html.Div(className='twelve columns', children=[
                        html.H5('Ordered Attribute Correlations'),
                        html.Div(id="pcp", children=[
                            dcc.Loading(
                                id="loading-2",
                                type="default",
                                children=[html.Div(id="loading-output-pcp"),
                                          dcc.Graph(id="pcp-graph", figure=pcp_fig)]
                            )
                        ])
                    ])
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
                    html.H5("Categorical Attribute Correlations", id='heatmap-val'),
                    dcc.Loading(
                        id="loading-4",
                        type="default",
                        children=[html.Div(id="loading-output-heatmap"),
                                  dcc.Graph(id='heatmap', figure=heatmap_fig)])
                ]
            ),
        ]
    )


    @app.callback(
        Output("heatmap-x-axis-dropdown", "options"),
        Input('heatmap-y-axis-dropdown', 'value'))
    def set_heatmap_x_dropdown_options(y_choice):
        """
        Used for the application callback that applies a custom rule to determine which dropdown options should be made
        available to the user. The custom rule is that since both the "X axis" dropdown and the "Y axis" dropdown offer
        the same attribute options by default, if an attribute is selected in either of these dropdowns, then it should
        be removed from the other. Additionally, if the "focused attribute" is "rating", then the "review rate
        number" attribute is removed from both dropdowns' options, since combining average rating and review rate number
        in the heatmap does not make sense semantically.
        :param y_choice: the value currently selected in the "Y axis" dropdown
        :param focused_attribute: the value of the selected focused attribute
        :return: the updated list of dropdown options
        """

        dropdown_options = []
        # for k, v in cat_attr_dict.items():
        #     if v == "review rate number" and focused_attribute == "rating":
        #         continue
        #
        #     if v != y_choice:
        #         dropdown_options.append({"label": k, "value": v})
        for option in cat_attr_list:
            if option != y_choice:
                dropdown_options.append(option)

        return dropdown_options


    @app.callback(
        Output("heatmap-y-axis-dropdown", "options"),
        Input('heatmap-x-axis-dropdown', 'value'))
    def set_heatmap_y_dropdown_options(x_choice, ):
        """
        Used for the application callback that applies a custom rule to determine which dropdown options should be made
        available to the user. The custom rule is that since both the "X axis" dropdown and the "Y axis" dropdown offer
        the same attribute options by default, if an attribute is selected in either of these dropdowns, then it should
        be removed from the other. Additionally, if the "focused attribute" is "rating", then the "review rate
        number" attribute is removed from both dropdowns' options, since combining average rating and review rate number
        in the heatmap does not make sense semantically.
        :param x_choice: the value currently selected in the "X axis" dropdown
        :param focused_attribute: the value of the selected focused attribute
        :return: the updated list of dropdown options
        """

        dropdown_options = []
        # for k, v in cat_attr_dict.items():
        #     if v == "review rate number" and focused_attribute == "rating":
        #         continue
        #
        #     if v != x_choice:
        #         dropdown_options.append({"label": k, "value": v})
        for option in cat_attr_list:
            if option != x_choice:
                dropdown_options.append(option)

        return dropdown_options


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


    @app.callback(
        Output("pcp-graph", "figure"),
        Output("loading-output-pcp", "children"),
        Input("select-focused-attribute", "value"),
        Input("establishment-size-checklist", "value"),
        Input('choropleth-mapbox', 'selectedData'),
        Input('pcp-checklist', 'value'))
    def update_pcp_view(focused_attribute, selected_establishment_sizes, selected_data, checklist_values):
        return update_pcp(cbp_df, focused_attribute, checklist_values, selected_data=selected_data,
                          selected_establishment_sizes=selected_establishment_sizes), None


    @app.callback(
        Output("heatmap", "figure"),
        Output("loading-output-heatmap", "children"),
        Input('choropleth-mapbox', 'selectedData'),
        Input("select-focused-attribute", "value"),
        Input("establishment-size-checklist", "value"),
        Input("heatmap-x-axis-dropdown", "value"),
        Input("heatmap-y-axis-dropdown", "value"),
        Input("aggregation-dropdown", "value"))
    def update_heatmap_view(selected_data, focused_attribute, selected_establishment_sizes, x_choice, y_choice,
                            aggregate_value):
        return update_heatmap(cbp_df,
                              focused_attribute,
                              x_choice=x_choice,
                              y_choice=y_choice,
                              aggregate_value=aggregate_value,
                              selected_data=selected_data,
                              selected_establishment_sizes=selected_establishment_sizes), None

    app.run_server(debug=True, dev_tools_ui=True)
