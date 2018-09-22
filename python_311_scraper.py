import requests
from bs4 import BeautifulSoup
import sys
import re
import pandas as pd
import urllib3
import datetime

urllib3.disable_warnings()  # Turns off the annoying warnings about certificates


### Functions ###

def get_a_single_page_of_data(page_number):
	
	starting_url = 'https://mobile311.sfgov.org/?external=false'
	if page_number > 1:
		url = starting_url + '&page=' + page_number
	else:
		url = starting_url
	response = requests.get(url, verify=False)   ### is this really bad to do?? ###
	html = response.content
	soup = BeautifulSoup(html, 'html.parser')

	# Pull out each entry
	info = soup.find_all('td', attrs={"class": "report-content"})

	info_dict = {}

	# Get important info from each entry and put into a dict
	for each_entry in info:
		# create unique identifier for each entry
		# find_all() returns a list, pop() undoes that and just gives the first and only item
		# not the best solution
		report_id = str(each_entry.find_all('span', attrs={"class": "activity-timestamp"}).pop()).translate(None, '\t\n ')[-15:-7]   

		# pull out specific event info
		report_title = each_entry.find_all('h2').pop().text.strip()
		report_description = each_entry.find_all('div').pop().text.strip()
		
		# store all in dict
		info_dict[report_id] = [report_title, report_description]

	return info_dict



### Run the script ###

full_info_dict = {}

# Load pre-existing data
all_data = 'all_data.txt'

# Cycle through all 20 pages of entries
for x in range(20):
	page_number = str(x + 1)
	info_dict = get_a_single_page_of_data(page_number)
	full_info_dict.update(info_dict)

# Merge new data and old data, save to data.txt file
df = pd.DataFrame.from_dict(full_info_dict, orient='index', columns=['Report_title', 'Report_description'])
all_data_df = pd.read_csv(all_data, sep='\t', index_col=0)
merged_data = all_data_df.append(df).drop_duplicates()
with open('all_data.txt', 'w') as f:
	merged_data.to_csv(f, encoding='utf-8', sep='\t')







