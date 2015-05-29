from bs4 import BeautifulSoup
import requests
from pprint import pprint
import yaml

pub28_base_url = 'http://pe.usps.gov/text/pub28/'
state_abbr_url = pub28_base_url + '28apb.htm'
street_suffix_url = pub28_base_url + '28apc_002.htm'

# requests fails with "too many redirects" on Pub28 site if User-Agent not set
headers = headers = {
    'Accept':'text/html', 
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36'
}

state_html = requests.get(state_abbr_url, headers=headers).content
state_soup = BeautifulSoup(state_html)

# Create state abbreviation to name mapping
state_table = state_soup.find(id='ep18684')
state_abbr_ps = state_table.find_all('p', class_='tbl9c')
state_name_ps = state_table.find_all('p', class_='tbl9')

state_abbrs = [p.a.text for p in state_abbr_ps]
state_names = [p.a.text for p in state_name_ps]

state_abbr_to_name = dict(zip(state_abbrs, state_names))

# Add Military "States" to abbreviation mapping
mil_table = state_soup.find(id='ep19241')
mil_abbr_ps = mil_table.find_all('p', class_='tbl9c')
mil_name_ps = mil_table.find_all('p', class_='tbl9')

mil_abbrs = [p.a.text for p in mil_abbr_ps]
mil_names = [p.a.text for p in mil_name_ps]

mil_abbr_to_name = dict(zip(mil_abbrs, mil_names))

state_abbr_to_name.update(mil_abbr_to_name)


# Create geographic direction mapping
geodir_table = state_soup.find(id='ep19168')
geodir_abbr_ps = geodir_table.find_all('p', class_='tbl9c')
geodir_name_ps = geodir_table.find_all('p', class_='tbl9')

geodir_abbrs = [p.a.text for p in geodir_abbr_ps]
geodir_names = [p.a.text for p in geodir_name_ps]

geodir_abbr_to_name = dict(zip(geodir_abbrs, geodir_names))


# Create street suffix mapping
street_suffix_html = requests.get(street_suffix_url, headers=headers).content
street_suffix_soup = BeautifulSoup(street_suffix_html)

# Create state abbreviation to name mapping
street_suffix_table = street_suffix_soup.find(id='ep533076')
street_suffix_trs = street_suffix_table.find_all('tr')

cur_suffix_abbr = None
street_suffix_map = {}

for tr in street_suffix_trs:
    tds = tr.find_all('td')

    if len(tds) == 3:
        suffix_name = tds[0].p.a.text.strip()
        suffix_alt = tds[1].p.a.text.strip()
        suffix_abbr = tds[2].p.a.text.strip()
        current_suffix_abbr = suffix_abbr

        street_suffix_map[suffix_abbr] = {'name': suffix_name, 'alt': [suffix_alt]}
    elif len(tds) == 1:
        suffix_alt = tds[0].p.a.text.strip()
        street_suffix_map[current_suffix_abbr]['alt'].append(suffix_alt)
    else:
        raise ValueError("BOOM")


output = {
    'states': state_abbr_to_name,
    'directions': geodir_abbr_to_name,
    'street_suffixes': street_suffix_map
}

stream = file('abbreviations.yaml', 'w')

output_yaml = yaml.safe_dump(output, stream, default_flow_style=False)

