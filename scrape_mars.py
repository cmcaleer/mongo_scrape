from flask import Flask, render_template
from bs4 import BeautifulSoup as bs
import requests
import os
from splinter import Browser
import cssutils
import pandas as pd
from tabulate import tabulate
import json 
import pymongo

app = Flask(__name__)

# setup mongo connection
conn = "mongodb://localhost:27017"
client = pymongo.MongoClient(conn)

# connect to mongo db and collection
#Create schema
marsDB = client["marsDB"]
#Drop artist collection
marsDB.scraped_data.drop()
#Create collection
mars_col = marsDB["scraped_data"]
executable_path = {'executable_path': 'chromedriver.exe'}

def scrape_info():
    "Main scrape functiona that will execute all other functions" 
    "and return a dictionary"

#     mars_info = {}

#     mars_info["news"] = marsNews()

#     mars_info["featured_image_url"] = marsFeaturedImageURL()

#     mars_info["weather"] = marsWeather()

#     mars_info["facts"] = marsFacts()

#     mars_info["mars_hemispheres"] = marsHems()
    mars_info={
                "news":marsNews(),
                "featured_image_url":marsFeaturedImageURL(),
                "weather":marsWeather(),
                "facts":marsFacts(),
                "mars_hemispheres":marsHems()
        }
 
  
    mars_col.insert(mars_info) 
        

def marsNews():

    page_link  = "https://mars.nasa.gov/news/8426/nasa-garners-7-webby-award-nominations/"
    page_response = requests.get(page_link, timeout=5)
    nasa_page_content = bs(page_response.content, "html.parser")

    nasa_title= nasa_page_content.title.text
    nasa_page_content.find_all("p")   
    nasa_textContent = []
    for i in range(0, 14):
        nasa_paragraphs = nasa_page_content.find_all("p")[i].text
        nasa_textContent.append(nasa_paragraphs)
    
    nasa_latest_news = nasa_textContent[0]
    news = f'Title:{nasa_title}, Latest News: {nasa_latest_news}'

    return news


def marsFeaturedImageURL():

    mars_browser = Browser('chrome', **executable_path, headless=False)

    mars_url="https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    mars_browser.visit(mars_url)
    mars_html = mars_browser.html
    mars_soup = bs(mars_html, 'html.parser')
    div_style = mars_soup.find('article')['style']
    style = cssutils.parseStyle(div_style)
    image_url = style['background-image']
    image_url = image_url.replace('url(', '').replace(')', '')

    #tag the ending to the base url
    featured_image_url = f'https://www.jpl.nasa.gov{image_url}'
    
    #convert to json for mongo import
    image_json=json.dumps(featured_image_url)
    #return featured_image_url
    return image_json
    mars_browser.quit()

def marsWeather():
    twitter_browser = Browser('chrome', **executable_path, headless=False)
    twitter_url = "https://twitter.com/marswxreport?lang=en"
    twitter_browser.visit(twitter_url)
    twitter_html = twitter_browser.html
    twitter_soup = bs(twitter_html, 'html.parser')

    #this will find the tweets about weather
    mars_weather=[]
    weather_info_list = []
    for weather_info in twitter_soup.find_all('p',class_="TweetTextSize TweetTextSize--normal js-tweet-text tweet-text"):
            weather_info_list.append(weather_info.text.strip())

    # Find the latest tweet about weather
    mars_weather = weather_info_list[0]

    #Clean up the data a little to remove excess data at end
    mars_weather = mars_weather[:-30]
    
    #convert to json for mongo import
    weather_json=json.dumps(mars_weather)
    #return featured_image_url
    return weather_json
    mars_browser.quit()
    #return mars_weather
    twitter_browser.quit()

def marsFacts():
    facts_url = "https://space-facts.com/mars/"
    #USE BS to scrape the table data from website and print as table string  
    facts = pd.read_html(facts_url)[0]
    facts.columns=["Description","Value"]
    facts.set_index("Description", inplace=True)

    return facts.to_html()
    

def marsHems():
    #set main url
    hem_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    #use browser to visist url
    hem_browser = Browser('chrome', **executable_path, headless=False)
    hem_browser.visit(hem_url)

    hem_html = hem_browser.html
    hem_soup = bs(hem_html, 'html.parser')
        
    # set open list to append images to
    hemisphere_image_urls = []

    products = hem_soup.find('div', class_='result-list')
    hemispheres = products.find_all('div', class_='item')
        
    #find the links to hemispheres, click, then browse those for imge url and append to open list
    for hemisphere in hemispheres:
        title = hemisphere.find('div', class_='description')

        title_text = title.a.text
        title_text = title_text.replace(' Enhanced', '')
        hem_browser.click_link_by_partial_text(title_text)

        hem_html = hem_browser.html
        hem_soup = bs(hem_html, 'html.parser')

        image = hem_soup.find('div', class_='downloads').find('ul').find('li')
        img_url = image.a['href']

        hemisphere_image_urls.append({'title': title_text, 'img_url': img_url})

        hem_browser.click_link_by_partial_text('Back')
    
    #convert to json for mongo import
    hems_json = json.dumps(hemisphere_image_urls)    
    return hems_json
    #return hemisphere_image_urls
    hem_browser.quit()
   
    hem_browser.quit()

   