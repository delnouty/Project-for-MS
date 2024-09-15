import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# Load the data using pandas
data = pd.read_csv('https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/Data%20Files/historical_automobile_sales.csv')

# Initialize the Dash app
app = dash.Dash(__name__)

# Set the title of the dashboard
app.title = "Automobile Statistics Dashboard"

# Create the dropdown menu options
dropdown_options = [
    {'label': 'Yearly Statistics', 'value': 'Yearly Statistics'},
    {'label': 'Recession Period Statistics', 'value': 'Recession Period Statistics'}
]
# List of years 
year_list = [i for i in range(1980, 2024, 1)]

# Define the color mapping
color_map = {
    'Supperminicar': '#006BA4',
    'Mediumfamilycar': '#FF800E',
    'Smallfamiliycar': '#ABABAB',
    'Sports': '#595959',
    'Executivecar': '#5F9ED1'
}

# Define the month order
month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

#Define the vihicle type order
vehicle_type_order = ['Mediumfamilycar','Smallfamiliycar', 'Supperminicar', 'Sports', 'Executivecar']

# Create the layout of the app
app.layout = html.Div([
    # Add title to the dashboard
    html.H1("Automobile Sales Dashboard", style={'textAlign': 'center','color':'#503D36','font-size':24}),
    # Add two dropdown menus
    html.Div([
        html.Label("Select Statistics:"),
        dcc.Dropdown(
            id='select-statistics',
            options=dropdown_options,
            value='Yearly Statistics',
            placeholder='Select a report type'
        )
    ], style={'width': '50%', 'display': 'inline-block', 'padding': '10px'}),
    html.Div([
        html.Label("Select Year:"),
        dcc.Dropdown(
        id='select-year',
        options=[{'label': i, 'value': i} for i in year_list],
        value=2020
    )], style={'width': '50%', 'display': 'inline-block', 'padding': '10px'}),
    html.Div(id='output-container', className='output-container', style={'padding': '10px'})
])

# Define the callback function to update the input container based on the selected statistics
@app.callback(
    Output(component_id='select-year', component_property='disabled'),
    Input(component_id='select-statistics', component_property='value')
)
def update_input_container(selected_statistics):
    if selected_statistics == 'Yearly Statistics':
        return False
    else:
        return True

# Define the callback function to update the output container based on the selected statistics and year
@app.callback(
    Output(component_id='output-container', component_property='children'),
    [Input(component_id='select-statistics', component_property='value'),
     Input(component_id='select-year', component_property='value')]
)
def update_output_container(selected_statistics, input_year):
    if selected_statistics == 'Recession Period Statistics':
        # Filter the data for recession periods
        recession_data = data[data['Recession'] == 1]
        
        # Get recession years
        recession_years = recession_data['Year'].unique()

        # Plot 1: Automobile sales fluctuate over Recession Period (year wise)
        yearly_rec = recession_data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        R_chart1 = dcc.Graph(
            figure=px.line(yearly_rec, 
                           x='Year',
                           y='Automobile_Sales',
                           title="Average Automobile Sales fluctuation over Recession Period")
            .update_layout(xaxis=dict(tickvals=recession_years,tickangle=-90))
        )

        # Plot 2: Calculate the average number of vehicles sold by vehicle type during recession period
        average_sales = recession_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
        R_chart2 = dcc.Graph(
            figure=px.bar(average_sales,
                          x='Vehicle_Type',
                          y='Automobile_Sales',
                          title="Average Number of Vehicles Sold by Vehicle Type during Recession Period",
                          color='Vehicle_Type',
                          color_discrete_map=color_map,
                          category_orders={'Vehicle_Type': vehicle_type_order})
        )

        # Plot 3: Pie chart for total expenditure share by vehicle type during recessions
        exp_rec = recession_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        R_chart3 = dcc.Graph(
            figure=px.pie(exp_rec, 
                          names='Vehicle_Type',
                          values='Advertising_Expenditure',
                          title="Total Expenditure Share by Vehicle Type during Recession")
        )
        R_chart3.figure.update_traces(marker=dict(colors=[color_map.get(i, '#000000') for i in exp_rec['Vehicle_Type']]))

        # Plot 4: Stacked bar chart for the effect of unemployment rate on vehicle type and sales
        unemp_data = recession_data.groupby(['unemployment_rate', 'Vehicle_Type'])['Automobile_Sales'].mean().reset_index()
        R_chart4 = dcc.Graph(
            figure=px.bar(unemp_data,
                          x='unemployment_rate',
                          y='Automobile_Sales',
                          color='Vehicle_Type',
                          barmode='stack',
                          labels={'unemployment_rate': 'Unemployment Rate', 'Automobile_Sales': 'Average Automobile Sales'},
                          title='Effect of Unemployment Rate on Vehicle Type and Sales',
                          color_discrete_map=color_map,
                          category_orders={'Vehicle_Type': vehicle_type_order})
        )

        return [
            html.Div(className='chart-item', children=[html.Div(children=R_chart1), html.Div(children=R_chart2)], style={'display': 'flex'}),
            html.Div(className='chart-item', children=[html.Div(children=R_chart3), html.Div(children=R_chart4)], style={'display': 'flex'})
        ]

    elif selected_statistics == 'Yearly Statistics' and input_year:
        yearly_data = data[data['Year'] == input_year]

        # Plot 1: Yearly Automobile sales using line chart for the whole period
        yas = data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        Y_chart1 = dcc.Graph(
            figure=px.line(yas,
                           x='Year',
                           y='Automobile_Sales',
                           title='Yearly Automobile Sales')
        )

        # Plot 2: Total Monthly Automobile sales using line chart
        mas = yearly_data.groupby('Month')['Automobile_Sales'].sum().reset_index()
        mas['Month'] = pd.Categorical(mas['Month'], categories=month_order, ordered=True)
        mas = mas.sort_values('Month')
        Y_chart2 = dcc.Graph(
            figure=px.line(mas,
                           x='Month',
                           y='Automobile_Sales',
                           title='Total Monthly Automobile Sales')
        )

        # Plot 3: Number of vehicles sold during the given year by vehicle type
        total_sales = yearly_data.groupby('Vehicle_Type')['Automobile_Sales'].sum().reset_index()
        Y_chart3 = dcc.Graph(
            figure=px.bar(total_sales,
                          x='Vehicle_Type',
                          y='Automobile_Sales',
                          title=f'Number of Vehicles Sold by Vehicle Type in {input_year}',
                          color='Vehicle_Type',
                          color_discrete_map=color_map,
                          category_orders={'Vehicle_Type': vehicle_type_order})
        )

        # Plot 4: Total Advertisement Expenditure for each vehicle type using pie chart
        exp_data = yearly_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        Y_chart4 = dcc.Graph(
            figure=px.pie(exp_data,
                          names='Vehicle_Type',
                          values='Advertising_Expenditure',
                          title=f'Total Advertisement Expenditure by Vehicle Type in {input_year}')
        )
        Y_chart4.figure.update_traces(marker=dict(colors=[color_map.get(i, '#000000') for i in exp_data['Vehicle_Type']]))

        return [
            html.Div(className='chart-item', children=[html.Div(children=Y_chart1), html.Div(children=Y_chart2)], style={'display': 'flex'}),
            html.Div(className='chart-item', children=[html.Div(children=Y_chart3), html.Div(children=Y_chart4)], style={'display': 'flex'})
        ]

    else:
        return None

# Run the Dash app
if __name__ == '__main__':
    app.run_server()
