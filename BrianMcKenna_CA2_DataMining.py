#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 11 18:24:05 2021

@author: brianmckenna
"""

from bs4 import BeautifulSoup, SoupStrainer
import requests	    
import pandas as pd
import os    
        
#Adverts.ie iPhone 11 adverts
main_url = 'https://www.adverts.ie/for-sale/mobile-phones-accessories/mobile-phones/apple/1122/q_iphone+11/list_view/'

# ******************* Scrape to get individual advert URLS **********

# Get urls for first 15 pages of the search results
page_urls = []
# example of url for each advert https://www.adverts.ie/apple/iphone-11/25413246 
# initialise array for the advert url links
advert_urls = []
pageNum = 1
numOfPages = 15
while pageNum <= numOfPages:
      url = '{}list-view/page-{}'.format(main_url,pageNum)
      adverts = SoupStrainer('div',{'class': 'posts list'})
      html = requests.get(url).text
      soup = BeautifulSoup(html, 'html.parser', parse_only=adverts)
      page_urls.append(url)
      pageNum = pageNum + 1
      
      # Find all adverts with a div with a class name of holder header to access the a tag
      # Need to extract individual advert urls so we can get as much info as possible
      for advert in soup.find_all("div", class_="holder header"):
          advert_url = 'https://www.adverts.ie' + advert.find('a').get('href')
          advert_urls.append(advert_url)

# ******************* Access each URL and get valuable information ************


askingPrices = []
locations = []
sellerType = []
storageSize = []
unlocked = []
possibleStorageSizes = ["64GB","64 GB","128GB", "128 GB","256GB", "256 GB"]


countPageNum = 1
for advert in advert_urls:
    html = requests.get(advert).text
    soup = BeautifulSoup(html, 'html.parser')
    print("Scraping data in progess...")
    # get the prices, also shows if they are a private seller or shop based on the buy now price
    if soup.find("span", class_="ad_view_info_cell price") is not None:
        price = soup.find("span", class_="ad_view_info_cell price").get_text(strip=True)
        sellerType.append("Private")
    elif soup.find("span", class_="ad_view_info_cell buynow_price") is not None:
        price = soup.find("span", class_="ad_view_info_cell buynow_price").get_text(strip=True)
        sellerType.append("Business")
    askingPrices.append(price)
    
    # get the locations
    locationTag = soup.find("dt", string="Location:")
    location = locationTag.find_next("dd").get_text(strip=True)
    town, county = location.split(", ")
    locations.append(county)
    
    # get the description
    line_in_description = []
    main_description = soup.find("div", class_="main-description")
    description = main_description.select("p:nth-of-type(2)")
    for text in description:
        stripped_text = text.get_text(strip = True)
        notFoundStorageCount = 0
        notFoundUnlockedCount = 0
        
        # loop through each possible storage size
        # check if each desc contains array values for possible storage sizes
        for i in possibleStorageSizes:  
            if i in stripped_text.upper():
                storageSize.append(i)
                break
            else:
                notFoundStorageCount = notFoundStorageCount + 1
             
            if notFoundStorageCount == len(possibleStorageSizes):
                storageSize.append("")
                
        
        # check if unlocked is in the description
        if "UNLOCKED" in stripped_text.upper():
            unlocked.append("TRUE")
            break
        else:
            notFoundUnlockedCount+=1
                
        if notFoundUnlockedCount > 0:
            unlocked.append("FALSE")
            
    
    
      
    
    
os.chdir('/Users/brianmckenna/Documents/College/Software Development/Year 3/Data Science/BrianMcKenna_CA_2/')

iPhoneDF=pd.DataFrame(list(zip(askingPrices, locations, sellerType, storageSize, unlocked)), columns=['Price', 'Location', 'Seller_Type', 'Storage_Size', 'Unlocked'])

iPhoneDF.to_csv('BrianMcKenna_iPhoneData_12DEC21.csv', index=False)

print("Complete")

