
# Import Splinter and BeautifulSoup

from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt

def scrape_all():
    # Initiate headless driver for deployment/ set up splinter
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "hemispheres": hemispheres(browser) 
    }

    # Stop webdriver and return data
    browser.quit()
    return data



def mars_news(browser):

    # Scrape Mars News
    # Visit the Mars NASA news site:

    url = 'https://redplanetscience.com'
    browser.visit(url)

    # Optional delay for loading the page

    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # HTML Parser/convert browser html to soup object then quit browser

    html = browser.html
    news_soup = soup(html, 'html.parser')
    
    # Add try/except for error handling
    
    try:

        slide_elem = news_soup.select_one('div.list_text')

        # Use the parent element to find the first `a` tag and save it as `news_title`

        news_title = slide_elem.find('div', class_='content_title').get_text()

        # Use the parent element to find the paragraph text

        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
    
    except AttributeError:
        return None, None
    
    return news_title, news_p



# ## JPL Space Images Featured Image

def featured_image(browser):

    # Visit URL

    url = 'https://mars.nasa.gov/msl/home/'
    # url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(url)

    # Find and click the full image button

    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup

    html = browser.html
    img_soup = soup(html, 'html.parser')
    
    # add try/except for error handling
    
    try:

        # Find the relative image url

        img_url_rel = img_soup.find('img', alt='slide 1 - Mars Curiosity Rover').get('src')
        # img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
        
    except AttributeError:
        return None

    # Use the base URL to create an absolute URL

    img_url = f'https://mars.nasa.gov/{img_url_rel}'
    # img_url = f'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/{img_url_rel}'
    
    return img_url

# ## Mars Facts

def mars_facts():
    
    # add try/except for error handling
    try:
        
        # use 'read_html" to scrape the facts table into a dataframe

        df = pd.read_html('https://data-class-mars-facts.s3.amazonaws.com/Mars_Facts/index.html')[0]
    
    except BaseException:
        return None
    

    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)


    # Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes="table table-striped")

def hemispheres(browser):
    
    # Use browser to visit the URL
    
    url = 'https://data-class-mars-hemispheres.s3.amazonaws.com/Mars_Hemispheres/index.html'
    browser.visit(url)
    
    # Create a list to hold the images and titles.

    hemisphere_image_urls = []
    
    # Write code to retrieve the image urls and titles for each hemisphere.
    
    try:
        for i in range(0, 4):

            # create empty dictionary to house title and URL
            hemispheres = {}

            # click link to full image
            image = browser.find_by_tag('h3')[i]
            image.click()

            # get Sample image url and add it to hemispheres dict
            html = browser.html
            hem_soup = soup(html, 'html.parser')
            img_url_rel = hem_soup.find('img', class_='thumb').get('src')
            hemispheres["img_url"] = f'https://data-class-mars-hemispheres.s3.amazonaws.com/Mars_Hemispheres/{img_url_rel}'

            # get title and add it to hemispheres dict
            hemispheres["title"] = hem_soup.find('h2').text

            # add dict to list initiated in Step 2
            hemisphere_image_urls.append(hemispheres)

            # return to original url to click next link
            browser.back()
            
    except BaseException:
        return None
    
    return hemisphere_image_urls



if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())
