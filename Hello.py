
import streamlit as st
from streamlit.logger import get_logger
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import plotly as plt
from plotly.express import choropleth


pop = pd.read_csv('population.csv')
data = pd.read_csv('life expectancy.csv')
df = pd.merge(data, pop, left_on=['Country Name', 'Year']
                     , right_on=['Entity', 'Year'])
df = df.drop('Entity', axis=1)
df = df.drop('Code', axis=1)
df['Life Expectancy Difference'] = df.groupby('Country Code')['Life Expectancy World Bank'].diff()
df['Communicable%'] = df['Communicable'] / df['Population (historical estimates)']
df['CO2/P'] = df['CO2'] / df['Population (historical estimates)']*1000

year_2000_data = df[df['Year'] == 2001]
year_2019_data = df[df['Year'] == 2019]

common_countries = set(year_2000_data['Country Name']).intersection(year_2019_data['Country Name'])

df['Life Expectancy Difference (2000-2019)'] = 0  # Initialize the new column

for country in common_countries:
    diff = year_2019_data[year_2019_data['Country Name'] == country]['Life Expectancy World Bank'].values[0] - \
           year_2000_data[year_2000_data['Country Name'] == country]['Life Expectancy World Bank'].values[0]
    df.loc[df['Country Name'] == country, 'Life Expectancy Difference (2000-2019)'] = diff
df = df.sort_values(by=['Country Name','Life Expectancy Difference (2000-2019)'], ascending=False)


LOGGER = get_logger(__name__)


def run():
    st.set_page_config(
        page_title="Hello",
        page_icon="👋",
    )
    # Create the Choropleth plot
    fig_world = go.Figure(data=go.Choropleth(
        locations=df['Country Name'],
        z=df['Life Expectancy World Bank'],
        locationmode='country names',
        colorscale='bluyl',
        colorbar_title="Scale",
        zmin=40,
        zmax=85,  
    ))
    years = df['Year'].unique()
    years.sort()
    
    # Create slider for the years
    slider_steps = []
    for year in years:
        step = {
            'label': str(year),
            'method': 'update',
            'args': [{'z': [df[df['Year'] == year]['Life Expectancy World Bank']], 'colorbar_title': 'Life Expectancy'}]}
        slider_steps.append(step)

    #Add Slider
    fig_world.update_layout(
        sliders=[{'active': 0, 'steps': slider_steps, 'x': 0.0, 'xanchor': 'left', 'y': 0, 'yanchor': 'top'}])

    #Add title
    fig_world.update_layout(title="World Map of Global Life Expectancy")
    st.plotly_chart(fig_world, use_container_width=True) 

    st.write("""
            Life expectancy is a critical indicator of a country's overall health and quality of life. The map above explores the trends in life expectancy from 2001 to 2019, showing how things might have changed in life expectancy across different countries. Some observations about the data:
            - Global Increase in Life Expectancy: Over the past two decades there has been a global increase in life expectancy. This is also reflecting improvements in healthcare and sanitation.
            - Regional Disparities: High-income countries generally have higher life expectancies than low-income countries. Sub-Saharan Africa in particular has faced challenges in improving life expectancy.
            - Economic Factors: Economic stability and development are closely linked to life expectancy. Countries with stable economies tend to have better healthcare systems and longer life expectancies. There have been notable changes in life expectancy during this period on the African continent.  
            """)
    
    #get the unemployment mean per region
    region_means = df.groupby(['Region', 'Year'])['Unemployment'].mean().reset_index()

    #make the line plot
    fig_line = px.line(region_means, x='Year', y='Unemployment', color='Region',
                         labels={'Unemployment': 'Mean Unemployment Rate', 'Year': 'Year'})

    #add titles and legend
    fig_line.update_layout(
        title='Unemployment rate per Region',
        xaxis_title='Year',
        yaxis_title='Mean Unemployment Rate',
        showlegend=True,
        legend_title_text='Region')
    
    st.plotly_chart(fig_line, use_container_width=True) 
    st.write("""Analyzing the unemployment rate per region from 2001 to 2019 using this lineplot we can see that there are some big global fluctuations. These fluctuations could be attributed to economic factors, recessions, growth etc. 
             There are also some regional varations. North America and Europe have a big spike around the 2008 recession in which the unemployment rate did go up quite a bit. 
             In Sub Saharen Africa there hasn't been a big change from 2001 to 2019. Examining the data over nearly two decades allows for the identification of long-term trends. Regions that consistently experience high or low unemployment rates may offer valuable insights into the factors contributing to their labor market dynamics.   
            """)
    
    fig = px.scatter(y = df['Prevelance of Undernourishment'], x = df['Life Expectancy World Bank'],
		animation_frame=df['Year'], color = df['Region'], hover_name = df['Country Name'],
		size = df['Population (historical estimates)'])
    fig.update_layout(
	    title = 'Scatterplot',xaxis_title="Life expectancy (years)", yaxis_title="Prevelance of Undernourishment (%)"
	)
    st.plotly_chart(fig, use_container_width=True)     

    # Scatter plot

    custom_colors = {
    'Low income': 'red',
    'Lower middle income': 'yellow',
    'Upper middle income': 'orange',
    'High income': 'green'
    }
    fig2 = px.scatter(df, 
                     x='Health Expenditure %', 
                     y='Life Expectancy World Bank', 
                     color='IncomeGroup',
                     color_discrete_map=custom_colors,  
                     opacity=0.4, 
                     title='Life Expectancy & Health Expenditure %')
    # Customize the layout
    fig2.update_layout(
        width=950,
        height=600,
        xaxis_title='Health Expenditure %',
        yaxis_title='Life Expectancy World Bank',
    )

    # Calculate the correlation
    correlation = df['Health Expenditure %'].corr(df['Life Expectancy World Bank'])
    st.write(f"Correlation between health expenditure and life expectancy: {correlation:.2f}")

    # Show the plot
    st.plotly_chart(fig2, use_container_width=True)     
    st.write("""The correlation between Prevalence of Undernourishment and the life expectancy is -0.69.  This can also be seen in this scatterplot.
There are a few clear conclusions that we can get from looking at the scatter plot between life expectancy and prevalence of undernourishment. The percentage of people that don’t get enough energy by eating is significantly getting smaller. The most countries of people that don’t eat enough are in Africa, this is as expected. We can also conclude the life expectancy is drastically increasing, more for African countries than for European and Asian countries.
""")    
    
    average_life_expectancy = df.groupby("IncomeGroup")["Life Expectancy World Bank"].mean().reset_index()
    fig_income = px.bar(average_life_expectancy, y="Life Expectancy World Bank", x="IncomeGroup", 
                       category_orders = {'IncomeGroup':['Low income', 
                                                          'Lower middle income', 'Upper middle income', 'High income']})

    fig_income.update_layout(title= 'Life expectancy per income group', xaxis_title = 'Income Group', yaxis_title = 'Life expectancy (Years)')
    st.plotly_chart(fig_income, use_container_width=True)  


# Functie om de plot te maken
    def create_plot(toon_data):
        if toon_data == 'Ja':
            fig5 = px.scatter(df, x='IncomeGroup', y='Life Expectancy World Bank', title='Zonder Health expenditure %')
        else:
            fig5 = px.scatter(df, x='IncomeGroup', y='Health Expenditure %', title='Met Health expenditure %')
        return fig5

 

    st.title('Interactieve Plot in Streamlit met Checkboxes')

 

# Creëer een interactieve plot met checkboxes
    toon_data = st.radio('Toon data:', ['Ja', 'Nee'])
    fig5 = create_plot(toon_data)
    st.plotly_chart(fig5, use_container_width=True)     
    st.write("""Without Health Expenditure %: This chart illustrates how life expectancy varies across different income groups without taking health expenditure into account.
    With Health Expenditure %: This chart illustrates the health expenditure across different income groups. It indicates whether there is a relationship between income group and health expenditure.
    The chart shows that people with different incomes have different life expectancies. It also seems that when a country spends more on healthcare, people tend to live longer. This suggests that putting money into healthcare can make people live longer. But remember, there are other things that can make a difference too.
    """)    

    diff = df.groupby('Country Name')['Life Expectancy Difference'].sum()
    diff = pd.DataFrame(diff)
    diff = diff.sort_values(by=['Life Expectancy Difference'], ascending=False)
    first_10_index_names= diff.index[:10]
    top10 = df[df['Country Name'].isin(first_10_index_names)]
    top10 = top10.sort_values(by=['Life Expectancy Difference (2000-2019)'], ascending=False)

    fig9 = px.bar(top10[top10['Year']==2019], x='Country Name', y='Life Expectancy Difference (2000-2019)',color = 'Region')
    st.plotly_chart(fig9, use_container_width=True)     

    top10 = top10.sort_values(by=['Year'], ascending=False)
    fig10 = px.line(top10, x='Year', y='Life Expectancy World Bank', color = 'Country Name')
    st.plotly_chart(fig10, use_container_width=True)  
    
    figa = px.line(top10, x='Year', y='Prevelance of Undernourishment', color = 'Country Name')
    st.plotly_chart(figa, use_container_width=True)  

    top10 = top10.sort_values(by=['Year'], ascending=False)
    figb = px.line(top10, x='Year', y='Communicable%', color = 'Country Name')
    st.plotly_chart(figb, use_container_width=True)  

 
 





if __name__ == "__main__":
    run()
