import json

import pandas as pd
import plotly.express as px
from dash import html, dcc

from config import focused_attr_dict
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
        print(selected_data)

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


# def update_heatmap(target_df, selected_data, focused_attribute, x_choice="review rate number", y_choice="room type", aggregate_value='avg'):
#     """
#     Used to update the heatmap figure
#     :param target_df: the dataframe containing the data that will be used by the choropleth figure
#     :param selected_data: contains the data points selected using the "lasso" or "box selection" tool of the choropleth
#     figure; None if no such selection is made
#     :param focused_attribute: the (quantitative) attribute of target_df we want to visualize on the heatmap using the colourmap
#     :param x_choice: the selected (categorical) attribute that will be visualized on the heatmap's X axis
#     :param y_choice: the selected (categorical) attribute that will be visualized on the heatmap's Y axis
#     :param aggregate_value: the selected aggregate function name that will be applied to the heatmap's data
#     :return:
#     """
#     # If a data selection is provided, filter target_df accordingly
#     if selected_data:
#         neighbourhoods = [x['location'] for x in selected_data['points']]
#         target_df = airbnb_df[airbnb_df['neighbourhood'].isin(neighbourhoods)]
#
#     heatmap_fig = px.density_heatmap(
#         data_frame=target_df, x=target_df[x_choice], y=target_df[y_choice],
#         z=target_df[attr_mapping_dict[focused_attribute]], histfunc=aggregate_value)
#     heatmap_fig.update_xaxes(dtick=1, fixedrange=True)
#     heatmap_fig.update_yaxes(fixedrange=True)
#     heatmap_fig.update_layout(margin=dict(r=2,b=4,t=10,l=3))
#
#     return heatmap_fig


if __name__ == '__main__':
    # Read the data from the csv file
    cbp_df = pd.read_csv(
        "../datasets/CBP_preprocessed.csv", low_memory=False)

    # Set the default focused attribute
    # TODO: Update this
    # default_focused_attr = list(focused_attr_dict.values())[0]

    default_focused_attr = "#Establishments"

    # Initialize choropleth figure
    choropleth_fig = update_choropleth(cbp_df, default_focused_attr)

    # Initialize histogram figure
    histogram_fig = update_histogram(cbp_df, default_focused_attr)

    # Initialize PCP figure
    pcp_fig = update_pcp(cbp_df, default_focused_attr, default_pcp_selections)

    # # Initialize heatmap figure
    # heatmap_fig = update_heatmap(airbnb_df, None, default_focused_attr)

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
                    # dcc.Loading(
                    #     id="loading-4",
                    #     type="default",
                    #     children=[html.Div(id="loading-output-heatmap"),
                    #               dcc.Graph(id='heatmap', figure=heatmap_fig)])
                ]
            ),
        ]
    )


    # @app.callback(
    #     Output("heatmap-x-axis-dropdown", "options"),
    #     Input('heatmap-y-axis-dropdown', 'value'),
    #     Input("select-focused-attribute", "value"))
    # def set_heatmap_x_dropdown_options(y_choice, focused_attribute):
    #     """
    #     Used for the application callback that applies a custom rule to determine which dropdown options should be made
    #     available to the user. The custom rule is that since both the "X axis" dropdown and the "Y axis" dropdown offer
    #     the same attribute options by default, if an attribute is selected in either of these dropdowns, then it should
    #     be removed from the other. Additionally, if the "focused attribute" is "rating", then the "review rate
    #     number" attribute is removed from both dropdowns' options, since combining average rating and review rate number
    #     in the heatmap does not make sense semantically.
    #     :param y_choice: the value currently selected in the "Y axis" dropdown
    #     :param focused_attribute: the value of the selected focused attribute
    #     :return: the updated list of dropdown options
    #     """
    #
    #     dropdown_options = []
    #     for k, v in cat_attr_dict.items():
    #         if v == "review rate number" and focused_attribute == "rating":
    #             continue
    #
    #         if v != y_choice:
    #             dropdown_options.append({"label": k, "value": v})
    #
    #     return dropdown_options
    #
    # @app.callback(
    #     Output("heatmap-y-axis-dropdown", "options"),
    #     Input('heatmap-x-axis-dropdown', 'value'),
    #     Input("select-focused-attribute", "value"))
    # def set_heatmap_y_dropdown_options(x_choice, focused_attribute):
    #     """
    #     Used for the application callback that applies a custom rule to determine which dropdown options should be made
    #     available to the user. The custom rule is that since both the "X axis" dropdown and the "Y axis" dropdown offer
    #     the same attribute options by default, if an attribute is selected in either of these dropdowns, then it should
    #     be removed from the other. Additionally, if the "focused attribute" is "rating", then the "review rate
    #     number" attribute is removed from both dropdowns' options, since combining average rating and review rate number
    #     in the heatmap does not make sense semantically.
    #     :param x_choice: the value currently selected in the "X axis" dropdown
    #     :param focused_attribute: the value of the selected focused attribute
    #     :return: the updated list of dropdown options
    #     """
    #
    #     dropdown_options = []
    #     for k, v in cat_attr_dict.items():
    #         if v == "review rate number" and focused_attribute == "rating":
    #             continue
    #
    #         if v != x_choice:
    #             dropdown_options.append({"label": k, "value": v})
    #
    #     return dropdown_options
    #
    # @app.callback(
    #     Output("heatmap-x-axis-dropdown", "value"),
    #     Output("heatmap-y-axis-dropdown", "value"),
    #     State("heatmap-x-axis-dropdown", "value"),
    #     State("heatmap-y-axis-dropdown", "value"),
    #     Input("select-focused-attribute", "value"))
    # def set_heatmap_dropdown_values(cur_x_value, cur_y_value, focused_attribute):
    #     """
    #     Used for the application callback that applies a custom rule to set the heatmap "X axis" and "Y axis" dropdown
    #     choices to specific values under certain conditions. Specifically, the custom rule is that if the "review rate
    #     number" is selected in either of the dropdowns and the "focused attribute" changes to "rating", the "X axis" and
    #     "Y axis" dropdowns values are set to "Room Type" and "District" respectively. This is done because the combination
    #     of "rating" (focused attribute) and "review rate number" (dropdowns) does not make sense semantically.
    #     :param cur_x_value: the value currently set to the "X axis" dropdown
    #     :param cur_y_value: the value currently set to the "Y axis" dropdown
    #     :param focused_attribute: the value of the selected focused attribute
    #     :return: the updated values for the "X axis" and "Y axis" dropdowns
    #     """
    #
    #     # Prevent "review rate number" being both the focused attribute and heatmap's x or y axis attribute
    #     if focused_attribute == "rating" and (cur_x_value == "review rate number" or cur_y_value == "review rate number"):
    #         return cat_attr_dict["Room Type"], cat_attr_dict["District"]
    #     else:
    #         return cur_x_value, cur_y_value
    #

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


    # @app.callback(
    #     Output("distr", "figure"),
    #     # Output("heatmap", "figure"),
    #     Output("loading-output-histogram", "children"),
    #     # Output("loading-output-heatmap", "children"),
    #     Input('choropleth-mapbox', 'selectedData'),
    #     Input("select-focused-attribute", "value"),
    #     # Input("heatmap-x-axis-dropdown", "value"),
    #     # Input("heatmap-y-axis-dropdown", "value"),
    #     Input("aggregation-dropdown", "value"))
    # def choropleth_mode_selection_changed(selected_data, focused_attribute, aggregate_func):
    # # def choropleth_mode_selection_changed(selected_data, focused_attribute, x_choice, y_choice, aggregate_value):
    #     # TODO: Also include heatmap update here!
    #     # return update_histogram(cbp_df, selected_data, focused_attribute), update_heatmap(cbp_df, selected_data, focused_attribute, x_choice, y_choice, aggregate_value), None, None
    #     return update_histogram(cbp_df, selected_data, focused_attribute), None

    # @app.callback(
    #     Output("heatmap-val", "children"),
    #     Input("select-focused-attribute", "value"),
    #     Input("heatmap-x-axis-dropdown", "value"),
    #     Input("heatmap-y-axis-dropdown", "value"),
    #     Input("aggregation-dropdown", "value"))
    # def update_heatmap_label(focused_attribute, x_choice, y_choice, aggregate_value):
    #     """
    #     Used to set the text of the heatmap idiom label
    #     :param focused_attribute: the selected focused attribute value
    #     :param x_choice: the "X axis" dropdown choice selected
    #     :param y_choice: the "Y axis dropdown choice selected
    #     :param aggregate_value: a value indicating the aggregate function selected
    #     :return: a string representing the heatmap idiom label
    #     """
    #     # Determine the wording based on which the heatmap label will be composed
    #     fa_name = [k for k, v in focused_attr_dict.items() if v == focused_attribute][0]
    #     x_name = [k for k, v in cat_attr_dict.items() if v == x_choice][0]
    #     y_name = [k for k, v in cat_attr_dict.items() if v == y_choice][0]
    #     aggr_labels = {'avg': ' Average', 'min': 'Min', 'max': 'Max'}
    #
    #     return "{}/{} group {} of {}".format(x_name, y_name, aggr_labels[aggregate_value], fa_name)
    #
    app.run_server(debug=True, dev_tools_ui=True)
