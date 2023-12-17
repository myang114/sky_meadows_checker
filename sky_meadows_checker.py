import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
'''Hello!

The Sky Meadows Checker checks the conditions needed to stargaze at Sky Meadows National Park in Virginia

There are 6 different conditions to look at when stargazing, Cloud Cover, Tranperency, Smoke, Wind, Humidity, and Temperature.

To use this program you need to select the current date up to 4 days in advanced, when you input a date make sure to not include dashes or spaces.
The date should just be for EX 20231216 or 20231217.
After you input a date, enter a file location where you want the csz data to be sent.

This program will webscrape https://www.cleardarksky.com/c/SkyMeadVAkey.html
using the diagram on the website it will section all the different sections into a list seperately.
using pandas it will all the data into a csv
'''

url = "https://www.cleardarksky.com/c/SkyMeadVAkey.html"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
# Send a GET request to the URL
# 10.1 You found a simple web page and described what data you wanted to scrape from it.
# 10.2 You used bs4 to scrape a simple web page.
response = requests.get(url, headers=headers)

data_by_date = {}

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Parse the HTML content of the page
    while True:
        day = input("Please enter a date as yyyymmdd no dashes or spaces")
        if len(day) == 8 and day.isdigit():
            break
        else:
            print("Please try again")
            continue

    while True:
        try:
            # 3.19 You read in user input from a file to use in your program
            userFile = input("Please input a file location for the data to be added to (make sure the file location exist)")
            break
        except FileNotFoundError:
            print("File not found please try again")
            continue
    # put all the website data into text form that we can search through
    soup = BeautifulSoup(response.text, 'html.parser')
    
    
    # Initialize a list to store all sections
    all_sections_list = []

    # Function to categorize coverage based on predefined sections
    def categorize_coverage(coverage_text):
        # list all the differeent sections needed to stargaze
        sections = {
            'Cloud Cover': ['Overcast', '90% covered', '80% covered', '70% covered', '60% covered', '50% covered',
                            '40% covered', '30% covered', '20% covered', '10% covered', 'Clear'],
            'Transparency': ['Too cloudy to forecast', 'Poor', 'Below Average', 'Average (', 'Above average', 'Transparent'],
            'Smoke': ['No Smoke', '2ug/m^3', '5ug/m^3', '10ug/m^3', '20ug/m^3', '40ug/m^3', '60ug/m^3', '80ug/m^3',
                    '100ug/m^3', '200ug/m^3', '500ug/m^3'],
            'Wind': ['>45 mph', '29 to 45 mph', '17 to 28 mph', '12 to 16 mph', '6 to 11 mph', '0 to 5 mph'],
            'Humidity': ['<25%', '25% to 30%', '30% to 35%', '35% to 40%', '40% to 45%', '45% to 50%', '50% to 55%',
                        '55% to 60%', '60% to 65%', '65% to 70%', '70% to 75%', '75% to 80%', '80% to 85%', '85% to 90%',
                        '90% to 95%', '95% to 100%'],
            'Temperature': ['< -40F', '-40F to -31F', '-30F to -21F', '-21F to -12F', '-12F to -3F', '-3F to 5F', '5F to 14F',
                            '14F to 23F', '23F to 32F', '32F to 41F', '41F to 50F', '50F to 59F', '59F to 68F', '68F to 77F',
                            '77F to 86F', '86F to 95F', '95F to 104F', '104F to 113F', '>113F']
        }

        for section, keywords in sections.items():
            for keyword in keywords:
                if keyword.lower() in coverage_text.lower():
                    return section
        # If coverage doesn't match any defined section add to seeing
        return 'Seeing'  

    # Function to add data to the all_sections_list
    def add_to_sections_list(date, time, coverage_text):
        coverage_section = categorize_coverage(coverage_text)

        all_sections_list.append({
            'Date': date,
            'Time': time,
            'Section': coverage_section,
            'Conditions': coverage_text
        })

    # Loop through the HTML and extract data
    for area in soup.find_all('area'):
        href = area.get('href')

        # Check if 'p=' exists in href
        #the href or image link has the date so the program will search the photo links for the date
        if href and 'p=' in href:
            date_index = href.find('p=') + 2
            date_length = 8

            # Check if the length is sufficient and date_index is valid
            if date_index > 0 and len(href) >= date_index + date_length:
                date = href[date_index:date_index + date_length]

                title = area.get('title')

                # Additional check for title and ':' in title
                # in the title after : there is a description
                if title and ':' in title:
                    time, description = title.split(': ', 1)

                    # Add data to the all_sections_list
                    #matching the despriction to the ones in the sectiosn 
                    #we can add them to each section
                    add_to_sections_list(date, time, description)

    # Convert the list to a DataFrame
    all_sections_df = pd.DataFrame(all_sections_list)
    # Create a Pandas DataFrame from the list of rows
    df = pd.DataFrame(all_sections_list)
     
     # 3.20 You wrote the results of a program out to a file
    df.to_csv(userFile + f'\{day}skyMeadows.csv')

else:
    #sometimes if you make too many request or the webstie detect suspituous
    #activites it will output a 406 or 400 or 506 error
    print(f"Failed to retrieve the page. Status code: {response.status_code}")

# Now you can access the data using the date as the key
if day in data_by_date:
    print(data_by_date[day])
    

