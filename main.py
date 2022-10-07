# python version = 3.10

import dash
import numpy as np

from dash import Dash, html, dcc,Input, Output
import dash_bootstrap_components as dbc

import plotly.express as px
import pandas as pd
import plotly.graph_objs as go

external_stylesheets = [dbc.themes.BOOTSTRAP]
app = Dash(__name__,external_stylesheets=external_stylesheets)

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
app.layout = html.Div([
    dbc.Row(dbc.Col(html.H1(children='FGC4 PWM API visualiser', ),width={"offset": 5},),

            ),
    dbc.Row([
        dbc.Col(
            children=[
            html.Div(children=[dcc.Input(id='cycles', value=30, type='number')," CLK Cycles: "]),
            html.Div(children=[dcc.Input(id='PRSC', value=1, type='number')," PRSC", ]),
            html.Div(children=[dcc.Input(id='FREQ', value=400, type='number'), " Clk F MHz", ]),
                ],

            width={"size": 2, "offset": 1},
        ),
        dbc.Col(
            children=[
                html.Div(children=[dcc.Input(id='CTRH', value=9, type='number')," CTRH: ",]),
                html.Div(children=[dcc.Input(id='CC0_I', value=4, type='number')," CC0:",]),

                html.Div(children=[dcc.Input(id='CC1_I', value=8, type='number')," CC1",]),

            ],
        width={"size": 2, "offset": -1},
        ),
        dbc.Col(children=[
            dcc.Checklist(id='inv_checkb',options=['Invert'])
        ], width={"size": 1},),
        dbc.Col(
            children=[
                html.Div(id='PWM_res_div',children=["PWM resolution: "]),
                html.Div(id='PWM_freq_div',children=["PWM frequency: "]),
                html.Div(id='PWM_DC_div',children=["PWM duty cycle: "]),
                html.Div(id='PWM_phs_div',children=["PWM phase: "]),

            ],
        width={"size": 3, "offset": -1},
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
    Output('PWM_res_div','children'),
    Output('PWM_freq_div','children'),
    Output('PWM_DC_div','children'),
    Output('PWM_phs_div','children'),
    Input('CC0_I', 'value'),
    Input('CC1_I', 'value'),
    Input('CTRH', 'value'),
    Input('PRSC', 'value'),
    Input('FREQ', 'value'),
    Input('inv_checkb','value')

)
def update_pwm_calcs(CC0, CC1, CTRH, PRSC, FREQ,invert):
    invert_ticked = invert is not None and 'Invert' in invert
    inputs = [CC0,CC1, CTRH, PRSC,FREQ]
    if PRSC == 0 :
        return ["Prescale value must be greater than or equal to 1 (= No prescaling"]*4
    for x in inputs:
        if x is None:
            return dash.no_update
    for x in inputs:
        if x<0:
            return ["Input cannot be negative"]*4

    resolution = (PRSC*1000)/FREQ
    frequency  = (1000*FREQ)/((CTRH+1)*PRSC)
    duty_cycle = -3

    if CC1 > CTRH and CC0 < CTRH:
        duty_cycle = (CTRH+1 - CC0)/(CTRH+1)
    if CC1 <= CTRH and CC0 <= CTRH and CC1>CC0:
        duty_cycle = (CC1-CC0)/(CTRH+1)
    if CC1 <= CTRH and CC1 <= CTRH and CC1==CC0:
        duty_cycle = (CTRH + 1 - CC0) / (CTRH + 1)
    if CC1 <= CTRH and CC1 <= CTRH and CC1<CC0:
        duty_cycle = (CTRH + 1 - CC0) / (CTRH + 1)
    if CC0 == 0 and CC1 > CTRH:
        duty_cycle = 1
    if CC1 == 0 and CC0 > CTRH:
        duty_cycle = 0
    if CC0 > CTRH:
        duty_cycle = 0
    if invert_ticked:
        duty_cycle = round(1- duty_cycle,10)
    resolution = "PWM resolution: " + str(resolution) + " ns"
    period     = "PWM frequency: " + str(frequency) + " KHz"
    duty_cycle = "PWM duty cycle " + str(duty_cycle)
    return resolution, period, duty_cycle, "Uncalculated"



@app.callback(
    Output(component_id='COUNTER_GRAPH', component_property='figure'),
    Output('PWM_O_GRAPH', 'figure'),
    Input('CC0_I','value'),
    Input('CC1_I','value'),
    Input('CTRH', 'value'),
    Input('cycles', 'value'),
    Input('PRSC','value'),
    Input('inv_checkb','value')
)
def updt_clk_graph(CC0, CC1, CTRH_i, cycles_i,prsc,invert):

    clksteps = 13
    if prsc is None or prsc==0:
        return dash.no_update
    if CTRH_i is not None and cycles_i is not None and CC0 is not None and CC1 is not None:
        pwm_df = pd.DataFrame({
            "CLK_COUNTER": range(clksteps*cycles_i),
            "Counter": [0] * cycles_i*clksteps,
            "PWM_OUT": [0] * cycles_i*clksteps,
        })
        print(invert)
        invert_ticked = invert is not None and 'Invert' in invert
        counter_val = 0
        pwm_out_pol = 0
        prsc_counter= 1
        for x in range(clksteps*cycles_i):
            pwm_df.at[x,"CLK_COUNTER"] =  x / clksteps
            pwm_df.at[x,"Counter", ] = counter_val

            if counter_val == CC0:
                pwm_out_pol = 1 if not invert_ticked else 0
            elif counter_val == CC1:
                pwm_out_pol = 0 if not invert_ticked else 1
            elif counter_val == 0:
                pwm_out_pol = 0 if not invert_ticked else 1
            pwm_df.at[x, "PWM_OUT"] = pwm_out_pol
            if x % clksteps == 0:
                prsc_counter = prsc_counter+1
                if prsc_counter % prsc == 0:
                    if counter_val == CTRH_i:
                        counter_val = 0
                    elif x != 0:
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