#-------------------------------------------------------------------------------
# Name:        crawler.py
# Purpose:     CS21A Assignment # 9 - implement a simple web crawler
#
# Author:      Jianfeng Sun
# Date:        11/24/2014
#-------------------------------------------------------------------------------
"""
implement a simple web crawler

Usage: crawler.py seed_url
seed: absolute url - the crawler will use it as the initial web address
"""
import urllib.request
import urllib.parse
import urllib.error
import urllib.robotparser
import re
import sys

# DO NOT CHANGE ok_to_crawl!!!
def ok_to_crawl(absolute_url):
    """
    check if it is OK to crawl the specified absolute url

    We are implementing polite crawling by checking the robots.txt file
    for all urls except the ones using the file scheme (these are urls
    on the local host and they are all OK to crawl.)
    We also use this function to skip over mailto: links and javascript: links.
    Parameter:
    absolute_url (string):  this is an absolute url that we would like to crawl
    Returns:
    boolean:  True if the scheme is file (it is a local webpage)
              True if we successfully read the corresponding robots.txt
                   file and determined that user-agent * is allowed to crawl
              False if it is a mailto: link or a javascript: link
                   if user-agent * is not allowed to crawl it or
                   if it is NOT an absolute url.
    """
    if absolute_url.lower().startswith('mailto:'):
        return False
    if absolute_url.lower().startswith('javascript:'):
        return False
    link_obj=urllib.parse.urlparse(absolute_url)
    if link_obj.scheme.lower().startswith('file'):
        return True
    # check if the url given as input is an absolute url
    if not link_obj.scheme or not link_obj.hostname:
        print('Not a valid absolute url: ', absolute_url)
        return False
    #construct the robots.txt url from the scheme and host name
    else:
        robot_url= link_obj.scheme+'://'+link_obj.hostname + '/robots.txt'
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(robot_url)
        try:
            rp.read()
        except:
            print ("Error accessing robot file: ", robot_url)
            return False
        else:
            return rp.can_fetch("*", absolute_url)

# DO NOT CHANGE crawl!!!
def crawl(seed_url):
    """
    start with the seed_url and crawl up to 10 urls

    Parameter:
    seed_url (string) - this is the first url we'll visit.
    Returns:
    set of strings - set of all the urls we have visited.
    """
    urls_tocrawl = {seed_url}  # initialize our set of urls to crawl
    urls_visited = set()  # initialize our set of urls visited
    while urls_tocrawl and len(urls_visited) < 10:
        current_url= urls_tocrawl.pop() # just get any url from the set
        if current_url not in urls_visited: # check if we have crawled it before
            page = get_page(current_url)     # call get_page to return html strings
            if page:
                more_urls = extract_links(current_url, page)    # call extract_links to get the links
                urls_tocrawl = urls_tocrawl | more_urls         # add them to be crawled
                urls_visited.add(current_url)
    return urls_visited

#------------Do not change anything above this line-----------------------------

def get_page(url):
    """
    get web page content from a given absolute url
    Parameter: an absolute url
    Return: a string that contains the web page content
    """
    try:
        with urllib.request.urlopen(url) as url_file:   # Use the with construct to open the url.
            text= url_file.read().decode('UTF-8')       # Assume the web page uses utf-8 encoding.
    except urllib.error.URLError as url_err:            # If there is an error opening the url
        print('Error opening url: ',url,url_err)      # print an error message and return an empty string.
        return ''
    except UnicodeDecodeError as decode_err:            # If there is an error decoding the content,
        print('Error decoding url: ',url,decode_err)  # print an error message and return an empty string.
        return ''
    else:
        return text       # and returns a string that contains the web page pointed to by that url.


def extract_links(base_url, page):
    """
    extract the links contained in the page at the base_url
    Parameters:
    base_url (string): the url we are currently crawling - web address
    page(string):  the content of that url - html
    Returns:
    A set of absolute urls (set of strings) - These are all the urls extracted
        from the current url and converted to absolute urls.

    """
    urls = set()         # 1. Initialize an empty set for the urls
    url_pattern = r'<a\s|\n+href\s|\n*=\s|\n*"(\S+)"\s*>' # 2. use a re pattern to extract the urls from the html file
    url_match = re.findall(url_pattern,page) # 3. make sure you extract ALL the URLs on that page
    for matches in url_match:
        if matches!=' ':                           # if the match is not empty string
            ab_url=urllib.parse.urljoin(base_url,matches)   # 4.convert each link to an absolute url
            if ok_to_crawl(ab_url)is True:              # 5. call the function ok_to_crawl to check if you are allowed
                urls.add(ab_url)         # 6. If that url is ok_to_crawl, add it to the set of urls found on that page.
            else:                                           # if not allowed
                continue                                   # continue without adding to the set
        else:                                # if the match is empty string
            continue                        # continue without convert
    return urls                     # 7. Return the set of absolute urls (set of strings)

def main():
    if len(sys.argv)!=2:
        print('usage: crawler.py seed_url')
    else:
        seed_url = sys.argv[1]    # 1.get the seed_url from the command line arguments
        crawl_path = crawl(seed_url)    # pass seed_url to crawl and save the set of urls to crawl_path
        with open('crawled.txt','w',encoding='utf-8')as out_file:   # 3.print out all the urls in crawl_path to
            for path in crawl_path:                   # a file called crawled.txt
                out_file.write(path+'\n')   # in the working directory. one url per line.
if __name__ == '__main__':
    main()