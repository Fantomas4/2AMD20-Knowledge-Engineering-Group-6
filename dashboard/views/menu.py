from dash import dcc, html

from dashboard.config import focused_attributes, def_state_ranking_weights


def generate_description_card():
    """
    
    :return: A Div containing dashboard title & descriptions.
    """
    return html.Div(id="title", children=[
        html.H5("USA Market Analysis"),
        html.Details([
            html.Summary('Help'),
            html.Div(id="description-card",
                     children=[
                         html.Div(
                             id="intro",
                             children=[
                                 "This dashboard offers an overview of data related το the software development business market in the USA,"
                                 "also integrating data related to the expertise and background of potential employees, such as university "
                                 "rankings."]
                         ),
                     ]),
        ])
    ])


def generate_control_card():
    """

    :return: A Div containing controls for graphs.
    """
    return html.Div(
        id="control-card",
        children=[
            html.Div(
                children=[
                    html.Label("Focused Attribute"),
                    dcc.Dropdown(
                        id="select-focused-attribute",
                        options=focused_attributes,
                        value=focused_attributes[0],
                        clearable=False
                    ),
                    html.Label("Establishment size:"),
                    dcc.Checklist(
                        id="establishment-size-checklist",
                        options=[{'label': '50-99 employees', 'value': 'Establishments with 50 to 99 employees'},
                                 {'label': '100-249 employees', 'value': 'Establishments with 100 to 249 employees'},
                                 {'label': '250-499 employees', 'value': 'Establishments with 250 to 499 employees'},
                                 {'label': '500-999 employees', 'value': 'Establishments with 500 to 999 employees'},
                                 {'label': '1000+ employees', 'value': 'Establishments with 1000 employees or more'}
                                 ],
                        value=['Establishments with 50 to 99 employees',
                               'Establishments with 100 to 249 employees',
                               'Establishments with 250 to 499 employees',
                               'Establishments with 500 to 999 employees',
                               'Establishments with 1000 employees or more']
                    )
                ]
            ),
            html.Div(
                children=[
                    html.Label("Ranking Score"),
                    html.Label("#Degree holders weight"),
                    dcc.Input(
                        id="score-weight-1",
                        type="number",
                        placeholder="Using default value: {}".format(def_state_ranking_weights["weight_1"]),
                        value=def_state_ranking_weights["weight_1"]),
                    html.Label("#Establishments weight"),
                    dcc.Input(
                        id="score-weight-2",
                        type="number",
                        placeholder="Using default value: {}".format(def_state_ranking_weights["weight_2"]),
                        value=def_state_ranking_weights["weight_2"])
                ], style={"margin-top": "15px"}
            )
        ], style={"textAlign": "float-left"}
    )


def make_menu_layout():
    return [generate_description_card(), generate_control_card()]
