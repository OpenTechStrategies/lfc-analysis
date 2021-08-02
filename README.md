# lfc-analysis
A repository for analysis tools for LFC + torque + Global View in order to create geographic visualizations of proposal data.  

# Setup Development Environment  
To set up the virtual environment use pipenv in command line:
```
pipenv install
```

# Using API  
Populate config file with API credentials including username and APIkey. Use the config_template.py file and replace username and api key with your own. Import config file in lfc_scripts.

```
username = "[USERNAME]"
api_key = "[API KEY]"
```

# Run script to generate map
The lfc_script.py file uses command line arguments to generate maps showing applicant locations based on competition.  
In the file directory run  
```console
python lfc_script.py [Competition key] [Color of map marker]  
```

The competition name keys should be one of the following: LLIIA2020, LFC100Change2020, LFC100Change2017, EO2020, RacialEquity2030, Climate2030, ECW2020, LoneStar2020

The colors can be one of the following: blue, red, black, purple  (For the full documentation of using colors in Folium, check https://python-visualization.github.io/folium/modules.html)  
