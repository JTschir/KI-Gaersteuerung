# https://dash.plotly.com/basic-callbacks
# https://dash-bootstrap-components.opensource.faculty.ai/docs/components/alert/

import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output
from store import ConfigStore

import sql_austausch as db

import plotly.express as px
import plotly.graph_objs as go
import pandas as pd

def run_server(configs):
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

    #-------------------- Tab-1 Konfiguration-------------------------

    from_tank_vol = dbc.FormGroup(
        [
            dbc.Label("Volumen des Gärtanks [m³]", html_for="tank_vol", width=3),
            dbc.Col(dbc.Input(id="tank_vol", type="number"), width=3),
        ],
        row=True,
    )

    form_wort_vol = dbc.FormGroup(
        [
            dbc.Label("Volumen der Würze [m³]", html_for="wort_vol", width=3),
            dbc.Col(dbc.Input(id="wort_vol", type="number"), width=3),
        ],
        row=True,
    )

    form_sw = dbc.FormGroup(
        [
            dbc.Label("Stammwürze [°P]", html_for="sw", width=3),
            dbc.Col(dbc.Input(id="sw", type="number"), width=3),
        ],
        row=True,
    )

    form_delta_goal = dbc.FormGroup(
        [
            dbc.Label("Ziel-Extraktabbau pro 24 Stunden [°P]", html_for="delta_goal", width=3),
            dbc.Col(dbc.Input(id="delta_goal", type="number"), width=3),
        ],
        row=True,
    )

    form_set_temperature = dbc.FormGroup(
        [
            dbc.Label("Solltemperatur für Angärphase [°C]", html_for="set_temperature", width=3),
            dbc.Col(dbc.Input(id="set_temperature", type="number"), width=3),
        ],
        row=True,
    )

    form_set_pressure = dbc.FormGroup(
        [
            dbc.Label("Solldruck für Angärphase [bar]", html_for="set_pressure", width=3),
            dbc.Col(dbc.Input(id="set_pressure", type="number"), width=3),
        ],
        row=True,
    )

    configTab = html.Div(
        [
            html.H2("Konfiguration"),
            dbc.Form([from_tank_vol, form_wort_vol, form_sw, form_delta_goal, form_set_temperature, form_set_pressure]),
            dbc.Button(id="btn_start", color="primary", className="mr-1")
        ],
        className="p-4"
    )


    @app.callback(
        [
            Output("tank_vol", "value"),
            Output("wort_vol", "value"),
            Output("sw", "value"),
            Output("delta_goal", "value"),
            Output("set_temperature", "value"),
            Output("set_pressure", "value")
        ],
        [
            Input("tank_vol", "value"),
            Input("wort_vol", "value"),
            Input("sw", "value"),
            Input("delta_goal", "value"),
            Input("set_temperature", "value"),
            Input("set_pressure", "value")
        ]
    )

    def update_config(input1, input2, input3, input4, input5, input6):
        # check if variables are unset (first callback)
        for x in [input1, input2, input3, input4, input5, input6]:
            if x is None:
                return [
                    configs.tank_vol, 
                    configs.wort_vol, 
                    configs.sw,             
                    configs.delta_goal, 
                    configs.set_temperature, 
                    configs.set_pressure
                    ]
        
        # else update internal store
        configs.tank_vol = input1
        configs.wort_vol = input2
        configs.sw = input3
        configs.delta_goal = input4
        configs.set_temperature = input5
        configs.set_pressure = input6

        return [
            configs.tank_vol, 
            configs.wort_vol, 
            configs.sw, 
            configs.delta_goal, 
            configs.set_temperature, 
            configs.set_pressure
            ]

    @app.callback(
        Output("btn_start", "children"),
        [Input("btn_start", "n_clicks")]
    )

    def start_stop_callback(n_clicks):
        if n_clicks is not None:
            configs.run_program = not configs.run_program
            
        return "Prozess Stoppen" if configs.run_program else "Prozess Starten"


    #---------------------- Tab-2 Dashboard --------------------------------

    form_flow_state = dbc.FormGroup(
        [
            dbc.Label("CO2-Durchfluss [l/30s]", html_for="flow_state", width=9),
            dbc.Col(dbc.Label(id="flow_state", width=15)),
        ],
        row=True,
    )

    form_extract_s = dbc.FormGroup(
        [
            dbc.Label("Extraktgehalt (scheinbar) [°P]", html_for="extract_s", width=9),
            dbc.Col(dbc.Label(id="extract_s", width=15)),
        ],
        row=True,
    )

    form_temperature = dbc.FormGroup(
        [
            dbc.Label("Temperatur [°C]", html_for="temperature", width=9),
            dbc.Col(dbc.Label(id="temperature", width=15)),
        ],
        row=True,
    )

    form_pressure = dbc.FormGroup(
        [
            dbc.Label("Druck [bar]", html_for="pressure", width=9),
            dbc.Col(dbc.Label(id="pressure", width=15)),
        ],
        row=True,
    )
    

    form_fermentation_state = dbc.FormGroup(
        [
            dbc.Label("Gärphase", html_for="fermentation_state", width=9),
            dbc.Col(dbc.Label(id="fermentation_state", width=15)),
        ],
        row=True,
    )

    form_extract_content = dbc.FormGroup(
        [
            dbc.Label("Extraktgehalt 24h", html_for="extract_content", width=9),
            dbc.Col(dbc.Label(id="extract_content", width=15)),
        ],
        row=True,
    )

    form_set_temperature = dbc.FormGroup(
        [
            dbc.Label("Solltemperatur [°C]", html_for="set_temperature_dash", width=9),
            dbc.Col(dbc.Label(id="set_temperature_dash", width=15)),
        ],
        row=True,
    )

    form_set_pressure = dbc.FormGroup(
        [
            dbc.Label("Solldruck [bar]", html_for="set_pressure_dash", width=9),
            dbc.Col(dbc.Label(id="set_pressure_dash", width=15)),
        ],
        row=True,
    )
    #----------- Daten Diagramme -----------------

    #Bislang nur für Extraktgehaltdiagramm, über plotly mehr einstellungsmöglichkeiten

    

    df_extract = {
        
        "Zeit [s]": db.read("Neue_Daten", "Zeit_Tage", " WHERE SudID=" + str(configs.fermentation_nr)),
        "Extraktgehalt": db.read("Neue_Daten", "Extraktgehalt_scheinbar_°P", " WHERE SudID=" + str(configs.fermentation_nr)),
    }

    df_co2 = pd.DataFrame({
        "Zeit [s]": db.read("Neue_Daten", "Zeit_Tage", " WHERE SudID=" + str(configs.fermentation_nr)),
        "CO2-Durchfluss": db.read("Neue_Daten", "CO2_Durchfluss_SL30s", " WHERE SudID=" + str(configs.fermentation_nr)),
    })

    df_temperatur = pd.DataFrame({
        "Zeit [s]": db.read("Neue_Daten", "Zeit_Tage", " WHERE SudID=" + str(configs.fermentation_nr)),
        "Temperatur": db.read("Neue_Daten", "Temperatur_°C", " WHERE SudID=" + str(configs.fermentation_nr)),
    })

    df_pressure = pd.DataFrame({
        "Zeit [s]": db.read("Neue_Daten", "Zeit_Tage", " WHERE SudID=" + str(configs.fermentation_nr)),
        "Druck": db.read("Neue_Daten", "Druck_bar", " WHERE SudID=" + str(configs.fermentation_nr)),
    })


    #fig_extract = px.line(df_extract, x="Zeit [s]", y="Extraktgehalt",title="Extraktgehalt (scheinbar)", width=1000, height=500)
    fig_extract = px.line(df_extract, x="Zeit [s]", y="Extraktgehalt",title="Extraktgehalt (scheinbar)", width=1000, height=500)

    fig_co2 = px.line(df_co2, x="Zeit [s]", y="CO2-Durchfluss",title="CO2-Durchfluss" , width=500, height=400)

    fig_temp = px.line(df_temperatur, x="Zeit [s]", y="Temperatur",title="Temperatur", width=500, height=400)

    fig_pres = px.line(df_pressure, x="Zeit [s]", y="Druck",title="Druck", width=500, height=400)

    #----------- Form Diagramme 1 ----------------

    form_diagrams = dbc.FormGroup(
        [
            dcc.Graph(
                    id="co2",
                    figure=fig_co2,
                ),
            dcc.Graph(
                    id="temperatur",
                    figure=fig_temp,
                ),
                dcc.Graph(
                    id="druck",
                    figure=fig_pres,
                ),
        ],
        row=True,

    )

    #-------------- Form Diagramme 2 ----------------------
    

    form_diagrams_extract = dbc.FormGroup(
        [
            dcc.Graph(
                    id="extrakt",
                    figure=fig_extract,
                ),
            dbc.Form([form_flow_state, form_temperature, form_pressure, form_extract_s, form_extract_content, form_fermentation_state, form_set_temperature, form_set_pressure]),
        ],
        row=True,

    )

    dashTab = html.Div(
        [
            html.H2("Dashboard"),
            dbc.Form([form_diagrams, form_diagrams_extract]),
            dcc.Interval(
                id='interval',
                interval=2*1000,    # [ms]
                n_intervals = 0
            )
        ],
        className="p-4"
    )


    @app.callback(
        [
            Output("flow_state", "children"),
            Output("temperature", "children"),
            Output("pressure", "children"),
            Output("extract_s", "children"),
            Output("extract_content", "children"),
            Output("fermentation_state", "children"),
            Output("set_temperature_dash", "children"),
            Output("set_pressure_dash", "children"),
              
        ],
        [
            Input("interval", "n_intervals")
        ]
    )

    def update_dash(n):
        return [
            configs.flow_dash,
            configs.temperature_dash,
            configs.pressure_dash,
            configs.extract_s_dash,
            configs.extract_delta24_dash,
            configs.phase_dash,
            configs.set_temperature_dash,
            configs.set_pressure_dash
            ]

    

    #-------------------- Layout --------------------------------


    app.layout = html.Div([
        html.H1("Gärprozess UI"),
        dbc.Tabs(
            [
                dbc.Tab(configTab, label="Konfiguration", tab_id="tab-1"),
                dbc.Tab(dashTab, label="Dash", tab_id="tab-2"),
            ],
            id="tabs",
            active_tab="tab-1",
        )
    ])

    app.run_server(debug=True)

if __name__ == "__main__":
    store = ConfigStore()
    run_server(store)