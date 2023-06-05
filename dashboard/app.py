import json

import pandas as pd
import plotly.express as px
from dash import html, dcc

from config import focused_attributes, def_state_ranking_weights
from main import app
from views.menu import make_menu_layout
from dash.dependencies import Input, Output


def enhance_df_with_state_ranking_score(target_df, score_weights):
    # Aggregate target_df to calculate the sum of #Establishments per State (regardless of business size)
    grouped_agg_df = target_df.groupby('State')['#Establishments'].sum()

    # Converting grouped, aggregated DataFrame to a dictionary
    state_establishment_count = grouped_agg_df.to_dict()

    # Aggregate target_df to retrieve the "Bachelor's Degree Holders" value per State, using the "first" aggregation
    grouped_agg_df = target_df.groupby('State')['Bachelor\'s Degree Holders'].first()

    # Converting grouped, aggregated DataFrame to a dictionary
    state_degree_holders_count = grouped_agg_df.to_dict()

    # Get all distinct State names from target_df
    distinct_state_values = target_df['State'].unique()

    # Create an empty score dataframe
    score_df = pd.DataFrame(columns=["State", "State Ranking Score"])

    for state in distinct_state_values:
        # Calculate the ranking score for the current state
        score = state_degree_holders_count[state] * score_weights["weight_1"] + \
                state_establishment_count[state] * score_weights["weight_2"]

        # Append the results to score_df
        score_df = score_df.append({"State": state, "State Ranking Score": score}, ignore_index=True)

    return pd.merge(target_df, score_df, on='State')


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


# def update_histogram(target_df, focused_attribute, selected_data=None, selected_establishment_sizes=None):
#     """
#     Used to update the histogram figure
#     :param target_df: the dataframe containing the data that will be used by PCP
#     :param focused_attribute: the attribute of target_df we want to visualize on PCP
#     :param selected_data: contains the data points selected using the "lasso" or "box selection" tool of the choropleth
#     figure; None if no such selection is made
#     :param selected_establishment_sizes: list containing the selected establishment size strings
#     :return: a figure object representing the generated histogram figure
#     """
#     # Filter target_df based on the selected establishment sizes
#     if selected_establishment_sizes is None:
#         selected_establishment_sizes = []
#     target_df = target_df[target_df['Business size'].isin(selected_establishment_sizes)]
#
#     if selected_data:
#         # If a data selection is provided, filter target_df accordingly
#         states = [x['location'] for x in selected_data['points']]
#         target_df = target_df[target_df['State code'].isin(states)]
#
#     fig = px.histogram(target_df[focused_attribute])
#     fig.update_xaxes(title="Value")
#     fig.update_yaxes(title="Count")
#     fig.update_layout(legend=dict(
#         orientation="h",
#         yanchor="bottom",
#         y=1.02,
#         xanchor="left",
#     ))
#     fig.update_layout(legend_title_text='Variable:', margin=dict(r=10, b=4, t=4, l=3))
#
#     return fig

# def update_scatter_plot(target_df, selected_data, focused_attribute, level, aggregation="mean"):


    # fig.add_trace(Scatter(
    #         x=selected_tsne[0],
    #         y=selected_tsne[1],
    #         mode="markers",
    #         marker={'color': 'red'},
    #         name="Selected Regions",
    #         hovertext=tsne_cities.index
    #     ))
    #
    # fig.update_layout(margin=dict(t=0, r=0, l=0, b=0))
    # fig.update_coloraxes(showscale=False)
    # return fig


if __name__ == '__main__':
    # Read the data from the csv file
    cbp_df = pd.read_csv(
        "../datasets/generated/final_preprocessed.csv", low_memory=False)

    # Set the default focused attribute
    default_focused_attr = focused_attributes[0]

    # Initialize choropleth figure
    choropleth_fig = update_choropleth(cbp_df, default_focused_attr)

    # # Initialize histogram figure
    # histogram_fig = update_histogram(cbp_df, default_focused_attr)

    # Initialize scatterplot figure
    scatterplot_fig = px.scatter(cbp_df, x="#Establishments", y="Bachelor\'s Degree Holders", color="Region")

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
                className="five columns",
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
                className="five columns",
                style={"padding": 0,
                       "background-color": 'rgba(0, 0, 255, 0.0)'},
                children=[
                    html.H5('#Establishments/#Degree holders/Region analysis'),
                    dcc.Graph(id='scatter-plot', figure=scatterplot_fig)
                ]
            )
            # Right column / histogram and heatmap
            # html.Div(
            #     id="right-column",
            #     className="three columns",
            #     style={"padding": 0,
            #            "background-color": 'rgba(0, 0, 255, 0.0)'},
            #     children=[
            #         html.H5('Ordered Attribute Distribution', id='attribute-label'),
            #         dcc.Loading(
            #             id="loading-3",
            #             type="default",
            #             children=[html.Div(id="loading-output-histogram"),
            #                       dcc.Graph(id='histogram', figure=histogram_fig)]
            #         ),
            #     ]
            # ),
        ]
    )


    @app.callback(
        Output("choropleth-mapbox", "figure"),
        Output("loading-output-choropleth", "children"),
        Input("select-focused-attribute", "value"),
        Input("aggregation-dropdown", "value"),
        Input("establishment-size-checklist", "value"),
        Input("score-weight-1", "value"),
        Input("score-weight-2", "value"))
    def update_choropleth_view(focused_attribute, aggregate_func, selected_establishment_sizes, score_weight_1, score_weight_2):
        # Generate a new dataframe using target_df that also includes the calculated ranking score for each state
        if score_weight_1 is None or score_weight_2 is None:
            # if either input is "None", use the default weights
            score_weight_1 = def_state_ranking_weights["weight_1"]
            score_weight_2 = def_state_ranking_weights["weight_2"]
        score_weights = {"weight_1": score_weight_1, "weight_2": score_weight_2}
        cbp_df_with_score = enhance_df_with_state_ranking_score(cbp_df, score_weights)

        return update_choropleth(cbp_df_with_score, focused_attribute, selected_establishment_sizes=selected_establishment_sizes,
                                 aggregation=aggregate_func), None


    # @app.callback(
    #     Output("histogram", "figure"),
    #     Output("loading-output-histogram", "children"),
    #     Input('choropleth-mapbox', 'selectedData'),
    #     Input("select-focused-attribute", "value"),
    #     Input("establishment-size-checklist", "value"),
    #     Input("score-weight-1", "value"),
    #     Input("score-weight-2", "value"))
    # def update_histogram_view(selected_data, focused_attribute, selected_establishment_sizes, score_weight_1, score_weight_2):
    #     # Generate a new dataframe using target_df that also includes the calculated ranking score for each state
    #     if score_weight_1 is None or score_weight_2 is None:
    #         # if either input is "None", use the default weights
    #         score_weight_1 = def_state_ranking_weights["weight_1"]
    #         score_weight_2 = def_state_ranking_weights["weight_2"]
    #     score_weights = {"weight_1": score_weight_1, "weight_2": score_weight_2}
    #     cbp_df_with_score = enhance_df_with_state_ranking_score(cbp_df, score_weights)
    #
    #     return update_histogram(cbp_df_with_score, focused_attribute, selected_data=selected_data,
    #                             selected_establishment_sizes=selected_establishment_sizes), None


app.run_server(debug=True, dev_tools_ui=True)
