from django.shortcuts import render
import folium 
import pandas as pd
import requests
import json
import os
import csv 
from pandas.io.json import json_normalize

# Create your views here.

def index(request):

    return render(request, 'pages/index.html')

def stats(request):

    country_geo = os.path.join(os.getcwd(),'countries.geo.json')

    url = "https://api.covid19api.com/summary"

    response = requests.request("GET", url)
    response_dict=response.json()

    df=json_normalize(response_dict['Countries'])
    df.to_csv('covid_data3.csv', index=False)

    covid_data=pd.read_csv('covid_data3.csv')
    confirmed_cases=covid_data['TotalConfirmed'].sum()

    # --------- Oman Total Cases ---------

    for i in range(1,len(response_dict['Countries'])):
        if response_dict['Countries'][i]['Country']=="Oman":
            index=i

    urlconf = "https://api.covid19api.com/country/Oman/status/confirmed/live"
    responseconf = requests.request("GET", urlconf)

    lineconf=responseconf.json()
    latest=len(lineconf)-1
    

    # Context variables to be passed to HTML

    confirmed=lineconf[latest]['Cases']
    deaths=response_dict['Countries'][index]['TotalDeaths']
    recovered1=response_dict['Countries'][index]['TotalRecovered']

    new_confirmed=response_dict['Countries'][index]['NewConfirmed']
    new_deaths=response_dict['Countries'][index]['NewDeaths']
    new_recovered=response_dict['Countries'][index]['NewRecovered']

    # ----- Comparison Top 3 COVID Affected Countries -------

    top=sorted(response_dict['Countries'], key=lambda x : x['TotalConfirmed'], reverse=True)[:4]

    countries_top3=[]
    cases_top3=[]

    for i in range(0, len(top)):

        countries_top3.append(top[i]['Country'])
        cases_top3.append(top[i]['TotalConfirmed'])

      #-------- GCC Countries -----
    
    top=sorted(response_dict['Countries'], key=lambda x : x['TotalConfirmed'], reverse=True)

    gcc=['Saudi Arabia', 'Kuwait', 'United Arab Emirates', 'Qatar', 'Bahrain', 'Oman']
    gcc_names=[]
    gcc_cases=[]
    for i in range(1,len(top)):
        if top[i]['Country'] in gcc:
            gcc_names.append(top[i]['Country'])
            gcc_cases.append(top[i]['TotalConfirmed'])

    # -------- Oman Trend --------
    url = "https://api.covid19api.com/country/Oman/status/confirmed/live"

    response = requests.request("GET", url)
    line_dict=response.json()

    dates=[]
    cases=[]

    for i in range (0,len(line_dict)):
        
        datestring=line_dict[i]['Date']
        date=datestring.split("T")
        dates.append(date[0])
        cases.append(line_dict[i]['Cases'])

        if(i==(len(line_dict)-1)):

            dou=date[0]
            tou=date[1]
# ------- Multi Line Trend Charts --------- #

    trendurl="https://pomber.github.io/covid19/timeseries.json"
    trend = requests.request("GET", trendurl)
    trend_dict=trend.json()

    countries=[]
    values=[]
    for key, value in trend_dict.items():
        countries.append(key)
        values.append(value)

    recovery=[]

    country_length=len(countries)
    val_length=len(values[1])

    for i in range(0,country_length):
        recovery.append([])
        for j in range(0, val_length):
                rec=values[i][j]['recovered']
                conf=values[i][j]['confirmed']

                if conf == 0:
                    recovery[i].append(0)
                else:
                    # print(i," ",j)
                    # print("Rec : ",rec)
                    # print("Confirmed : ",confirmed)
                    percent=round((float(rec)/conf)*100,2)
                    # print("Percent : ",percent,"\n\n\n\n")
                    recovery[i].append(percent) 

    lineplot_names=['Oman', 'United Arab Emirates', 'Spain', 'China','Italy', 'US']
    indices=[]

    for i in range(0,6):
        
        if lineplot_names[i] in countries:
            
            indices.append(countries.index(lineplot_names[i]))
    
    # countrydate=[]

    # for i in range (0,len(values[0])):

    #     countrydate.append(values[0][i]['date'])


    oman_recovery=recovery[indices[0]]
    uae_recovery=recovery[indices[1]]
    spain_recovery=recovery[indices[2]]
    china_recovery=recovery[indices[3]]
    italy_recovery=recovery[indices[4]]
    us_recovery=recovery[indices[5]]

    # ----- Growth Chart -------

    # gcc=['Saudi Arabia', 'Kuwait', 'United Arab Emirates', 'Qatar', 'Bahrain', 'Oman']
    gcc_indices=[]

    for i in range(0,6):   
        if gcc[i] in countries:  
            gcc_indices.append(countries.index(gcc[i]))

    Saudi_growth=[]
    Kuwait_growth=[]
    UAE_growth=[]
    Qatar_growth=[]
    Bahrain_growth=[]
    Oman_growth=[]

    for i in range(0, len(values[12])):
        
        Saudi_growth.append(values[gcc_indices[0]][i]['confirmed'])
        Kuwait_growth.append(values[gcc_indices[1]][i]['confirmed'])
        UAE_growth.append(values[gcc_indices[2]][i]['confirmed'])
        Qatar_growth.append(values[gcc_indices[3]][i]['confirmed'])
        Bahrain_growth.append(values[gcc_indices[4]][i]['confirmed'])
        Oman_growth.append(values[gcc_indices[5]][i]['confirmed'])

    # ------- Choropleths --------#

    # Total Confirmed Cases 

    m = folium.Map(tiles="cartodbpositron", max_bounds=True, no_wrap = True, min_zoom=2, max_zoom=18, location=[21.4735, 55.9754], zoom_start=6)

    folium.Choropleth( 

        geo_data=country_geo,
        name='choropleth',
        data=covid_data,
        columns=['Country', 'TotalConfirmed'],
        key_on='feature.properties.name',
        fill_color='Reds',
        fill_opacity=0.7,
        line_opacity=0.2,
        nan_fill_color = 'white',
        legend_name='COVID Confirmed', 

    ).add_to(m)

    folium.TileLayer('cartodbdark_matter').add_to(m)
    map_html = m._repr_html_()

    # Total Deaths

    death = folium.Map(tiles="cartodbpositron", max_bounds=True, no_wrap = True, min_zoom=2, max_zoom=18,location=[21.4735, 55.9754], zoom_start=6)

    folium.Choropleth( 

        geo_data=country_geo,
        name='choropleth',
        data=covid_data,
        columns=['Country', 'TotalDeaths'],
        key_on='feature.properties.name',
        fill_color='Reds',
        fill_opacity=0.7,
        line_opacity=0.2,
        nan_fill_color = 'white',
        legend_name='COVID Deaths', 

    ).add_to(death)

    folium.TileLayer('cartodbdark_matter').add_to(death)
    death_html = death._repr_html_()

    # Recovered

    recovered = folium.Map(tiles="cartodbpositron", max_bounds=True, no_wrap = True, min_zoom=2, max_zoom=18, location=[21.4735, 55.9754], zoom_start=6)

    folium.Choropleth( 

        geo_data=country_geo,
        name='choropleth',
        data=covid_data,
        columns=['Country', 'TotalRecovered'],
        key_on='feature.properties.name',
        fill_color='Greens',
        fill_opacity=0.7,
        line_opacity=0.2,
        nan_fill_color = 'white',
        legend_name='COVID Recovered', 

    ).add_to(recovered)

    folium.TileLayer('cartodbdark_matter').add_to(recovered)
    recovered_html = recovered._repr_html_()

    context={

        
        'map_html':map_html,
        'death_html':death_html,
        'recovered_html':recovered_html,
        'confirmed_cases':confirmed_cases,
        'confirmed':confirmed,
        'deaths':deaths,
        'recovered1':recovered1,
        'new_confirmed':new_confirmed,
        'new_deaths':new_deaths,
        'new_recovered':new_recovered,
        'countries_top3':countries_top3, 
        'cases_top3':cases_top3, 
        'gcc_names':gcc_names,
        'gcc_cases':gcc_cases, 
        'dates': dates,
        'cases':cases,
        'spain_recovery':spain_recovery,
        'oman_recovery':oman_recovery,
        'uae_recovery':uae_recovery,
        'china_recovery':china_recovery, 
        'italy_recovery':italy_recovery,
        'us_recovery':us_recovery, 
        'Saudi_growth':Saudi_growth,
        'Kuwait_growth':Kuwait_growth,
        'UAE_growth':UAE_growth,
        'Bahrain_growth':Bahrain_growth,
        'Qatar_growth':Qatar_growth,
        'Oman_growth':Oman_growth,
        'dou':dou, 
        'tou':tou
        
    }

    return render(request, 'pages/stats.html', context)