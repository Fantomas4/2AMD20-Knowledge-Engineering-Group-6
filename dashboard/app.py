import json
import warnings

import pandas as pd
import plotly.express as px
from dash import html, dcc

from config import focused_attributes, def_state_ranking_weights
from main import app
from views.menu import make_menu_layout
from dash.dependencies import Input, Output

warnings.filterwarnings("ignore", category=FutureWarning)


def enhance_df_with_state_ranking_score(target_df, score_weights):
    # Aggregate target_df to calculate the sum of #Establishments per State (regardless of business size)
    grouped_agg_df = target_df.groupby('State')['#Establishments'].sum()

    # Converting grouped, aggregated DataFrame to a dictionary
    state_establishment_count = grouped_agg_df.to_dict()

    # Aggregate target_df to retrieve the "Bachelor's Degree Holders" value per State, using the "first" aggregation
    grouped_agg_df = target_df.groupby('State')['#Bachelor\'s degree holders'].first()

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


def update_choropleth(target_df, focused_attribute):
    """
    Used to update the choropleth figure
    :param target_df: the dataframe containing the data that will be used by the choropleth figure
    :param focused_attribute: the attribute of target_df we want to visualize on the choropleth
    :param selected_establishment_sizes: list containing the selected establishment size strings
    :param aggregation: string that defines the aggregation we want to apply to our data within the choropleth
    :return: a figure object representing the generated choropleth figure
    """
    # Perform the required "sum" aggregations for specific attributes
    target_df["#Establishments"] = target_df.groupby("State")["#Establishments"].transform("sum")
    target_df["#Bachelor\'s degree holders"] = target_df.groupby("State")["#Bachelor\'s degree holders"].transform("sum")

    fig = px.choropleth(data_frame=target_df,
                        locations="State code",
                        locationmode="USA-states",
                        hover_name="State",
                        scope="usa",
                        color=focused_attribute,
                        color_continuous_scale='greens',
                        hover_data=["#Establishments",
                                    '#Bachelor\'s degree holders',
                                    'Men to women degree holders ratio',
                                    '(Mid)Senior to total ratio',
                                    '#(Mid)Senior degree holders']
                        )
    fig.update_layout(margin=dict(t=0, r=0, l=0, b=0))

    return fig


def update_scatter_plot(target_df):
    # Perform the required "sum" aggregations for specific attributes
    target_df["#Establishments"] = target_df.groupby("State")["#Establishments"].transform("sum")
    target_df["#Bachelor\'s degree holders"] = target_df.groupby("State")["#Bachelor\'s degree holders"].transform("sum")
    target_df["#Science and Engineering degree holders"] = target_df.groupby("State")["#Science and Engineering degree holders"].transform("sum")
    target_df["#Science and Engineering Related Fields degree holders"] = target_df.groupby("State")["#Science and Engineering Related Fields degree holders"].transform("sum")
    target_df["#Business degree holders"] = target_df.groupby("State")["#Business degree holders"].transform("sum")
    target_df["#Education degree holders"] = target_df.groupby("State")["#Education degree holders"].transform("sum")
    target_df["#Arts, Humanities and Others degree holders"] = target_df.groupby("State")["#Arts, Humanities and Others degree holders"].transform("sum")

    fig = px.scatter(target_df,
                     x="#Establishments",
                     y="#Bachelor\'s degree holders",
                     color="Region",
                     hover_data=["Region",
                                 "State",
                                 "#Establishments",
                                 '#Bachelor\'s degree holders',
                                 '#Science and Engineering degree holders',
                                 '#Science and Engineering Related Fields degree holders',
                                 '#Business degree holders',
                                 '#Education degree holders',
                                 '#Arts, Humanities and Others degree holders',
                                 'Men to women degree holders ratio',
                                 '(Mid)Senior to total ratio',
                                 '#(Mid)Senior degree holders']
                     )

    return fig


if __name__ == '__main__':
    # Read the data from the csv file
    cbp_df = pd.read_csv(
        "../datasets/generated/final_preprocessed.csv", low_memory=False)

    # Set the default focused attribute
    default_focused_attr = focused_attributes[0]

    # Initialize choropleth figure - ATTENTION: Make sure to use a deep copy of the original dataset!
    choropleth_fig = update_choropleth(cbp_df.copy(), default_focused_attr)

    # Initialize scatterplot figure
    scatterplot_fig = update_scatter_plot(cbp_df.copy())

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
                    dcc.Loading(
                        id="loading-2",
                        type="default",
                        children=[html.Div(id="loading-output-scatter-plot"),
                                  dcc.Graph(id='scatter-plot', figure=scatterplot_fig)]
                    ),
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
        Input("establishment-size-checklist", "value"),
        Input("score-weight-1", "value"),
        Input("score-weight-2", "value"))
    def update_choropleth_view(focused_attribute, selected_establishment_sizes, score_weight_1, score_weight_2):
        # Create a deep copy of the original dataframe which can be freely modified for this callback
        original_df = cbp_df.copy()

        # Filter target_df based on the selected establishment sizes
        if selected_establishment_sizes is None:
            selected_establishment_sizes = []
        processed_df = original_df[original_df['Business size'].isin(selected_establishment_sizes)]
        # print("===============================================================================================")
        # print("=============DIAG cbp_df")
        # print(cbp_df.to_markdown())
        #
        # print("=============DIAG original_df")
        # print(original_df.to_markdown())

        # Only calculate the state ranking score if filtered_df is NOT empty
        if not processed_df.empty:
            # Generate a new dataframe using target_df that also includes the calculated ranking score for each state
            if score_weight_1 is None or score_weight_2 is None:
                # if either input is "None", use the default weights
                score_weight_1 = def_state_ranking_weights["weight_1"]
                score_weight_2 = def_state_ranking_weights["weight_2"]
            score_weights = {"weight_1": score_weight_1, "weight_2": score_weight_2}
            processed_df = enhance_df_with_state_ranking_score(processed_df, score_weights)

        # print("=============DIAG processed_df")
        # print(processed_df.to_markdown())
        return update_choropleth(processed_df, focused_attribute), None


    @app.callback(
        Output("scatter-plot", "figure"),
        Output("loading-output-scatter-plot", "children"),
        # Input("degree-field-dropdown", "value"),
        Input("establishment-size-checklist", "value"))
    def update_scatter_plot_view(selected_establishment_sizes):
        # Create a deep copy of the original dataframe which can be freely modified for this callback
        original_df = cbp_df.copy()

        # Filter target_df based on the selected establishment sizes
        if selected_establishment_sizes is None:
            selected_establishment_sizes = []
        processed_df = original_df[original_df['Business size'].isin(selected_establishment_sizes)]

        return update_scatter_plot(processed_df), None

app.run_server(debug=True, dev_tools_ui=True)
