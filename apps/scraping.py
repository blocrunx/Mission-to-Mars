#!/usr/bin/env python
# coding: utf-8

import pandas as pd
# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup
import datetime as dt

def scrape_all():
   # Initiate headless driver for deployment
   browser = Browser("chrome", executable_path="chromedriver", headless=False)
   news_title, news_paragraph = mars_news(browser)
   
   # Run all scraping functions and store results in dictionary
   data = {
      "news_title": news_title,
      "news_paragraph": news_paragraph,
      "featured_image": featured_image(browser),
      "facts": mars_facts(),
      "last_modified": dt.datetime.now(),
      "pole_images": chal_images(browser)
   }
   return data

# Path to chromedriver
# executable_path = {'executable_path': 'chromedriver'}

# Automated browser to be passed to mars_news
# browser = Browser('chrome', **executable_path, headless=False)


def mars_news(browser):

    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=10)

    html = browser.html
    news_soup = BeautifulSoup(html, 'html.parser')

    # Add try for error handling
    try:
        slide_elem = news_soup.select_one('ul.item_list li.slide')

        # Use the parent element to find the first <a> tag and save it as `news_title`
        news_title = slide_elem.find("div", class_='content_title').get_text()
    
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_="article_teaser_body").get_text()

    except AttributeError:
        return None, None 

    return news_title, news_p 



# ### Featured Images

def featured_image(browser):

    # Visit URL
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)


    # Find and click the full image button
    full_image_elem = browser.find_by_id('full_image')
    full_image_elem.click()

    # Find the more info button and click that
    browser.is_element_present_by_text('more info', wait_time=10)
    more_info_elem = browser.find_link_by_partial_text('more info')
    more_info_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = BeautifulSoup(html, 'html.parser')

    try: 
        # Find the relative image url
        img_url_rel = img_soup.select_one('figure.lede a img').get("src")
        
    except AttributeError:
        
        return None


    # Use the base URL to create an absolute URL
    img_url = f'https://www.jpl.nasa.gov{img_url_rel}'

    return img_url

def mars_facts():
    
    try:
        # Use 'read_html" to scrape the facts table into a dataframe
        df = pd.read_html('http://space-facts.com/mars/')[0]

    except BaseException:
        return None    

    # Assign columns and set index of dataframe    
    df.columns=['Description', 'Value']
    df.set_index('Description', inplace=True)
    
    # Convert dataframe into HTML format, add bootstrap
    return df.to_html()



def chal_images(browser):
    #browser = Browser("chrome", executable_path="chromedriver", headless=False)
    # Visit URL
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    html = browser.html
    chal_soup = BeautifulSoup(html, 'html.parser')

    image_list = []
    some_list = []
    
    for a in chal_soup.find_all('a', href=True):
        some_list.append(a['href'])

    test = 'map/Mars'
    thumb_list =  []
    for list_item in some_list:
        if (test in list_item) and (list_item not in thumb_list):
            thumb_list.append(list_item)
    # build urls
    image_list = []
    for address in thumb_list:
        
        # Navigate to the page where image src is located
        target_url = f'https://astrogeology.usgs.gov{address}'
        browser.visit(target_url)
        html = browser.html
        
        # Parse soup to locate src
        current_soup = BeautifulSoup(html, 'html.parser')
        relative_image_url = current_soup.find('img', {'class':'wide-image'}).get('src')
        
        # Combine relative url with base to get full image url
        full_image_url = f'https://astrogeology.usgs.gov{relative_image_url}'

        # Add complete url to list of urls
        image_list.append(full_image_url)
    
    return image_list
        

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())