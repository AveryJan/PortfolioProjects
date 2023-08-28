"""
This application creates an interactive dashboard using Dash and Plotly. The purpose of the dashboard is to extract data on US domestic airline flights from a US airline reporting carrier on-time performance dataset available on Data Asset Exchange. The extracted data can be used to analyze the performance of the reporting airlines so that they can improve fight reliability, thereby improving customer reliability. A user can select either 'Yearly Airline Performance Report' or 'Yearly Airline Delay Report' for a year chosen. Each report consists of five graphs. A PDF file regarding this application can be found in the folder of this application on GitHub. 

Airline Reporting Carrier On-Time Performance Dataset:
The Reporting Carrier On-Time Performance Dataset contains information on approximately 200 million domestic US flights reported to the United States Bureau of Transportation Statistics. The dataset contains basic information about each flight (such as date, time, departure airport, arrival airport) and, if applicable, the amount of time the flight was delayed and information about the reason for the delay. This dataset can be used to predict the likelihood of a flight arriving on time. The CSV file of the dataset can be found in the folder of this application on GitHub.

Note: Before running this application, pandas and dash need to be installed using the command: pip3 install pandas dash

Author: Avery Jan 
Date: 8-20-2023
"""

# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import plotly.express as px
from dash import no_update


# Create a dash application
app = dash.Dash(__name__)

# Clear the layout and do not display exception till callback gets executed
app.config.suppress_callback_exceptions = True

# Read the airline data into pandas dataframe
airline_data =  pd.read_csv('https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/Data%20Files/airline_data.csv',
                            encoding = "ISO-8859-1",
                            dtype={'Div1Airport': str, 'Div1TailNum': str,
                                   'Div2Airport': str, 'Div2TailNum': str})


# Create a list of years
year_list = [i for i in range(2005, 2021, 1)]

"""Define a function that gathers data for creating the graphs relevant to a yearly airline performance report 

Function: For each of the five performance metrics, extract the data from the airline data and compute the sum or mean wherever necessary

Argument:

    df: airline_data 

Returns:
   Five dataframes, each containing the data about a specific performance metric
"""
def compute_data_choice_1(df):
    # Cancellation Category Count
    bar_data = df.groupby(['Month','CancellationCode'])['Flights'].sum().reset_index()
    # Average flight time by reporting airline
    line_data = df.groupby(['Month','Reporting_Airline'])['AirTime'].mean().reset_index()
    # Diverted Airport Landings
    div_data = df[df['DivAirportLandings'] != 0.0]
    # Source state count
    map_data = df.groupby(['OriginState'])['Flights'].sum().reset_index()
    # Destination state count
    tree_data = df.groupby(['DestState', 'Reporting_Airline'])['Flights'].sum().reset_index()
    return bar_data, line_data, div_data, map_data, tree_data


"""Define a function that gathers data for creating the graphs relevant to a yearly airline delay report

Function: For each of the five delay categories, extract the delay data from the airline data and compute their monthly average 

Argument:
    df: airline_data

Returns:
    Five dataframes, each contianing the monthly averages of a delay category 
"""
def compute_data_choice_2(df):
    # Compute delay averages
    avg_car = df.groupby(['Month','Reporting_Airline'])['CarrierDelay'].mean().reset_index()
    avg_weather = df.groupby(['Month','Reporting_Airline'])['WeatherDelay'].mean().reset_index()
    avg_NAS = df.groupby(['Month','Reporting_Airline'])['NASDelay'].mean().reset_index()
    avg_sec = df.groupby(['Month','Reporting_Airline'])['SecurityDelay'].mean().reset_index()
    avg_late = df.groupby(['Month','Reporting_Airline'])['LateAircraftDelay'].mean().reset_index()
    return avg_car, avg_weather, avg_NAS, avg_sec, avg_late


# Define the application layout
app.layout = html.Div(children=[
                                # Add title to the dashboard
                                html.H1('US Domestic Airline Flights Performance',
                                style={'textAlign': 'center', 'color': '#503D36', 'font-size': 24}),
                                # Dropdown creation begins here
                                # Create an outer division for the two dropdowns
                                html.Div([
                                    # Add an division for selecting the report type
                                    html.Div([
                                        # Create an division for adding dropdown helper text for report type
                                        html.Div(
                                            [
                                            html.H2('Report Type:', style={'margin-right': '2em'}),
                                            ]
                                        ),
                                        # Add a dropdown for the report types
                                        dcc.Dropdown(id='input-type',
                                                     options=[{'label': 'Yearly Airline Performance Report', 'value': 'OPT1'},{'label': 'Yearly Airline Delay Report', 'value': 'OPT2'}],
                                                     placeholder='Select a report type',
                                                     style={'width': '80%','padding':'5px', 'font-size': '20px', 'text-align-last':'center'}),
                                            # Place the helper text and the dropdown next to each other using the division tags attribute 'style'
                                            ], style={'display':'flex'}),

                                    # Add another division for selecting the year
                                    html.Div([
                                        # Create an division for adding dropdown helper text for choosing year
                                        html.Div(
                                            [
                                            html.H2('Choose Year:', style={'margin-right': '2em'})
                                            ]
                                        ),
                                        # Add a dropdown for the years
                                        dcc.Dropdown(id='input-year',
                                                     # Update dropdown values using the list of years created above
                                                     options=[{'label': i, 'value': i} for i in year_list],
                                                     placeholder="Select a year",
                                                     style={'width':'80%', 'padding':'3px', 'font-size': '20px', 'text-align-last' : 'center'}),
                                            # Place them next to each other using the division tag's attribute 'style'
                                            ], style={'display': 'flex'}),
                                          ]),

                                # Create empty divisions to for displaying computed graphs (plot1, plot2, plot3, plot4, and plot5)
                                # Create an empty division for plot1 and assign 'plot1' as the id 
                                html.Div([ ], id='plot1'),
                                # Create an outer division for plot2 and plot3
                                html.Div([
                                        # Create inner divisions for plot2 and plot3 and assign 'plot2' and 'plot3' as their id's
                                        html.Div([ ], id='plot2'),
                                        html.Div([ ], id='plot3')
                                # Place plot2 and plot3 next to each other using the division tag's attribute 'style'    
                                ], style={'display': 'flex'}),

                                # Create an outer division for plot4 and plot5 
                                html.Div([
                                         # Create inner divisions for plot4 and plot5 and assign 'plot4' and 'plot5' as their id's
                                        html.Div([ ], id='plot4'),
                                        html.Div([ ], id='plot5')
                                # Place plot4 and plot5 next to each other using the division tag's attribute 'style'   
                                ], style={'display': 'flex'}),
                                ])

# Define the callback function
@app.callback( [
                Output(component_id='plot1', component_property='children'),
                Output(component_id='plot2', component_property='children'),
                Output(component_id='plot3', component_property='children'),
                Output(component_id='plot4', component_property='children'),
                Output(component_id='plot5', component_property='children')
                ],
               [Input(component_id='input-type', component_property='value'),
                Input(component_id='input-year', component_property='value')],
               # Holding output state till user enters all the form/report information. In this case, it will be report type and year
               [State("plot1", "children"), State("plot2", "children"),
                State("plot3", "children"), State("plot4", "children"),
                State("plot5", "children")
               ])
# Add computation of graph data to callback function, create the graphs, and return the graphs to the empty divisions defined in the layout
def get_graph(chart, year, children1, children2, c3, c4, c5):

        # Select data
        df =  airline_data[airline_data['Year']==int(year)]

        if chart == 'OPT1': # 'OPT1' means user requests a 'Yearly Airline Performance Report'
            # Compute required information for creating graphs from the airline data
            bar_data, line_data, div_data, map_data, tree_data = compute_data_choice_1(df)

            # Create a bar chart that shows the number of flights under different cancellation categories
            bar_fig = px.bar(bar_data, x='Month', y='Flights', color='CancellationCode', title='Monthly Flight Cancellation')

            # Create a line chart that shows the average flight time per reporting airline
            line_fig = px.line(line_data, x='Month', y='AirTime', color='Reporting_Airline', title='Average monthly flight time (minutes) by airline')
            # Create a pie chart that shows the percentage of diverted airport landings per reporting airline
            pie_fig = px.pie(div_data, values='Flights', names='Reporting_Airline', title='% of flights by reporting airline')

            # Create a choropleth map chart that shows the number of flights flying from each state
            map_fig = px.choropleth(map_data,  # Input data
                    locations='OriginState',
                    color='Flights',
                    hover_data=['OriginState', 'Flights'],
                    locationmode = 'USA-states', # Set to plot as US States
                    color_continuous_scale='GnBu',
                    range_color=[0, map_data['Flights'].max()])
            map_fig.update_layout(
                    title_text = 'Number of flights from origin state',
                    geo_scope='usa') # Plot only the USA instead of globe

            # Create a treemap that shows the number of flights flying to each state from each reporting airline
            tree_fig = px.treemap( tree_data, path=['DestState', 'Reporting_Airline'],
                      values='Flights',
                      color='Flights',
                      color_continuous_scale='RdBu',
                      title='Flight count by airline to destination state'
                )


            # Return dcc.Graph components to those empty divisions defined in the application layout
            return [dcc.Graph(figure=tree_fig),
                    dcc.Graph(figure=pie_fig),
                    dcc.Graph(figure=map_fig),
                    dcc.Graph(figure=bar_fig),
                    dcc.Graph(figure=line_fig)
                   ]
        else:
            # User selects 'OPT2', meaning that user requests a 'Yearly Airline Delay Report'
            # Compute required information for creating graphs from the airline data
            avg_car, avg_weather, avg_NAS, avg_sec, avg_late = compute_data_choice_2(df)

            # Create five line graphs that show the monthly average delay by delay category per reporting airline for the given year  
            carrier_fig = px.line(avg_car, x='Month', y='CarrierDelay', color='Reporting_Airline', title='Average carrrier delay time (minutes) by airline')
            weather_fig = px.line(avg_weather, x='Month', y='WeatherDelay', color='Reporting_Airline', title='Average weather delay time (minutes) by airline')
            nas_fig = px.line(avg_NAS, x='Month', y='NASDelay', color='Reporting_Airline', title='Average NAS delay time (minutes) by airline')
            sec_fig = px.line(avg_sec, x='Month', y='SecurityDelay', color='Reporting_Airline', title='Average security delay time (minutes) by airline')
            late_fig = px.line(avg_late, x='Month', y='LateAircraftDelay', color='Reporting_Airline', title='Average late aircraft delay time (minutes) by airline')

            
            # Return dcc.Graph components to those empty divisions defined in the application layout
            return[dcc.Graph(figure=carrier_fig),
                   dcc.Graph(figure=weather_fig),
                   dcc.Graph(figure=nas_fig),
                   dcc.Graph(figure=sec_fig),
                   dcc.Graph(figure=late_fig)]


# Run the app
if __name__ == '__main__':
    app.run_server()
