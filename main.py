# python version = 3.10

import dash
import numpy as np

from dash import Dash, html, dcc,Input, Output
import dash_bootstrap_components as dbc

import plotly.express as px
import pandas as pd
import plotly.graph_objs as go


app = Dash(__name__)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
df = pd.DataFrame({
    "CLK_COUNTER": range(100),
    "CLK" : range(100),
    "PWM_COUNTER": range(100),
    "PWM_O": range(100),
})

CLK_GRAPH = go.Figure(data=[go.Scatter(x=df["CLK_COUNTER"], y=df["CLK"])])
COUNTER_GRAPH = go.Figure(data=[go.Scatter(x=df["CLK_COUNTER"], y=df["PWM_COUNTER"])])
PWM_O_GRAPH = go.Figure(data=[go.Scatter(x=df["CLK_COUNTER"], y=df["PWM_O"])])
app.layout = html.Div(children=[
    html.H1(children='PWM visualiser'),
    dbc.Row(
        [
            dbc.Col(
                html.Div(children=["CLK Cycles: ", dcc.Input(id='cycles', value=30, type='number')]),
                width={"size": 3, "order": "last", "offset": 1},
            ),
            dbc.Col(
                html.Div(["CTRH: ", dcc.Input(id='CTRH', value=10, type='number')]),
                width={"size": 3, "order": 1, "offset": 2},
            ),
            dbc.Col(
                html.Div(["Counter compare 0: ", dcc.Input(id='CC0_I', value=0, type='number')]),
                width={"size": 3, "order": 5},
            ),
            dbc.Col(
                html.Div(["Counter compare 1: ", dcc.Input(id='CC1_I', value=0, type='number')]),
                width={"size": 3, "order": 5},
            ),
        ]
    ),






    dbc.Row(dbc.Col(children=dcc.Graph(id='COUNTER_GRAPH', figure=CLK_GRAPH))
    ),
    dbc.Row(dbc.Col(children=dcc.Graph(id='PWM_O_GRAPH', figure=PWM_O_GRAPH
    )
    ))

])

@app.callback(
    Output(component_id='COUNTER_GRAPH', component_property='figure'),
    Output('PWM_O_GRAPH', 'figure'),
    Input('CC0_I','value'),
    Input('CC1_I','value'),
    Input('CTRH', 'value'),
    Input('cycles', 'value'),
)
def updt_clk_graph(CC0, CC1, CTRH_i, cycles_i):
    clksteps = 30
    if CTRH_i is not None and cycles_i is not None and CC0 is not None and CC1 is not None:
        pwm_df = pd.DataFrame({
            "CLK_COUNTER": range(clksteps*cycles_i),
            "Counter": [0] * cycles_i*clksteps,
            "PWM_OUT": [0] * cycles_i*clksteps,
        })
        counter_val = -1
        pwm_out_pol = 0
        for x in range(clksteps*cycles_i):
            pwm_df.at[x,"CLK_COUNTER"] =  x / clksteps
            pwm_df.at[x,"Counter", ] = counter_val

            if counter_val == CC0:
                pwm_out_pol = 1
            elif counter_val == CC1:
                pwm_out_pol = 0
            elif counter_val == CTRH_i:
                pwm_out_pol = 0
            pwm_df.at[x, "PWM_OUT",] = pwm_out_pol
            if (x % clksteps == 0):
                if counter_val == CTRH_i:
                    counter_val = 0
                else:
                    counter_val = counter_val + 1

    else:
        return dash.no_update
    counter_figure = px.line(pwm_df, x="CLK_COUNTER", y="Counter")
    counter_figure.update_layout(title="Counter value vs Pre-scaled clock cycle", xaxis_title="Prescaled clock cycle",
                                 yaxis_title="PWM Counter Value",title_x=0.5)

    PWM_figure = px.line(pwm_df, x="CLK_COUNTER", y="PWM_OUT")
    PWM_figure.update_layout(title="PWM Output signal", xaxis_title="Pre-scaled clock cycle",
                                 yaxis_title="PWM output signal", title_x=0.5)

    return counter_figure, PWM_figure





if __name__ == '__main__':
    app.run_server(debug=True)