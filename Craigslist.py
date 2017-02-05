
# coding: utf-8

# In[1]:

import requests
from bs4 import BeautifulSoup


# In[35]:

def fetch(query = None, auto_make_model = None, min_auto_year = None, max_auto_year = None, s=0):
    search_params = {key: val for key, val in locals().items() if val is not None}
    if not search_params: 
        raise ValueError("No valid keywords")
        
    base = "http://boston.craigslist.org/search/cto"
    resp = requests.get(base, params=search_params, timeout=3)
    resp.raise_for_status()
    return resp.content, resp.encoding


# In[4]:

def parse(html, encoding='utf-8'):
    parsed = BeautifulSoup(html, from_encoding=encoding)
    return parsed


# In[33]:

def extract_listings(parsed):
    listings = parsed.find_all('p', class_='result-info')
    extracted = []
    for listing in listings:
        title = listing.find('a', class_='result-title hdrlnk')
        price = listing.find('span', class_='result-price')
        try:
            price_string = price.string.strip()
        except AttributeError:
            price = ''
        location = listing.find('span', class_='result-hood')
        try:
            loc_string = location.string.strip()[1:-1].split()[0]
        except AttributeError:
            loc_string = ''
        this_listing = {
            'link': title.attrs['href'],
            'description': title.string.strip(),
            'price': price_string,
            'location': loc_string
        }
        extracted.append(this_listing)
    return extracted


# In[36]:

listings = []
for i in range(0, 500, 100):
    car_results = fetch(auto_make_model="honda civic", min_auto_year=2000, max_auto_year=2016, s=i)
    doc = parse(car_results[0])
    listings.extend(extract_listings(doc))


# In[212]:

print len(listings)


# In[17]:

print doc.prettify()


# In[430]:

import pandas as pd
import numpy as np


# In[457]:

df = pd.DataFrame(data=listings)


# In[444]:

import re

def get_mileage(description):
    description = description.lower().split('k miles')
    if len(description) == 1:
        description = description[0].split('000 miles')
        if len(description) == 1:
            try:
                description = re.search('(\d{1,3})k', description[0]).groups()
            except:
                return np.nan
    mileage = re.sub('[^0-9]', '', description[0].split()[-1])
    try:
        mileage = int(mileage) * 1000
        return mileage
    except:
        return np.nan


# In[458]:

df['mileage'] = df.apply(lambda row: get_mileage(row['description']), axis=1)
df


# In[469]:

def get_year(description):
    description = re.split('(20[0-9][0-9])', description)
    if len(description) == 1:
        description = re.split('([0-1][0-9])', description[0])
    try:
        return int(description[1]) if len(description[1]) == 4 else int('20' + description[1])
    except:
        return np.nan


# In[470]:

df['year'] = df.apply(lambda row: get_year(row['description']), axis=1)
df


# In[499]:

def get_standard_location(location):
    """
    Use first 5 characters of location in order to group. Gets rid of much of the weird stuff
    """
    if len(location) < 5:
        return location.lower()
    else:
        return location[:5].lower()

df['std_location'] = df.apply(lambda row: get_standard_location(row['location']), axis=1)
df['region'] = df['link'].str[1:4]
df


# In[472]:

import seaborn
import matplotlib.pyplot as plt
get_ipython().magic(u'matplotlib inline')


# In[473]:

df['price'] = df['price'].str[1:].astype(int)
df


# In[511]:

ax = df.plot('year', ['mileage', 'price'], secondary_y='price', legend=True, style='.', markersize=10, xlim=[1999,2017], title='Mileage and Price vs Year for Used Honda Civics, 2000-2016')
fig = ax.get_figure()
fig.savefig('mileage_and_price.pdf')


# In[475]:

plt.plot(df['price'], df['mileage'], linestyle='', marker='.')


# In[477]:

regions = df.groupby('region').mean()


# In[478]:

print df.groupby('region').count()


# In[493]:

regions = regions.append(pd.Series(data={'year': np.mean(df['year']), 'price': np.mean(df['price']), 'mileage': np.mean(df['mileage'])}, name='avg'))


# In[494]:

regions


# In[498]:

regions['price'].plot.bar()


# In[506]:

from scipy.stats import linregress


# In[508]:

print linregress(df['mileage'][~df['price'].isnull()].dropna(), df['price'][~df['mileage'].isnull()].dropna())
print linregress(df['year'][~df['price'].isnull()].dropna(), df['price'][~df['year'].isnull()].dropna())
print linregress(df['year'][~df['mileage'].isnull()].dropna(), df['mileage'][~df['year'].isnull()].dropna())


# In[ ]:


