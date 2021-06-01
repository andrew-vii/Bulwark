# Email Webscraper

import os
import sys
import requests
import json
import time
import _thread
import datetime
import argparse

# Check our input (single URL or file) 
def check_input(URL):
  if os.path.isfile(URL):
    print("Loaded - URL List Mode")
    input_type = 2
  elif "http" or "www" or "://" in URL:
    print("Loaded - Single URL Mode")
    input_type = 1
  else:
    print("URL Input Error")
    input_type = 0
    
  return input_type

# Check that we can reach the URL
def check_URL(URL, input_type):
  url_list = []
  status = 0
  if input_type == 1:
    print("Checking Single URL (" + URL + ")...")
    url_list.append(URL)
    check_response = requests.get(url_list[0] + "/")
    
    if check_response.status_code == 200:
      print("URL Confirmed Reachable!")
      status = 1
    else:
      print("Error Reaching URL")
      print("Error Received: " + str(check_response.status_code))
      status = 0 

  elif input_type == 2:
    print("Checking list of URLs to reach")
    with open(URL) as f:
      url_list = f.readlines()
      url_dictionary = { url.strip() : 0 for url in url_list }
    for c in url_list:
      i = c.strip()
      print("Checking " + i.strip() + "...")
      check_url = i.strip()
      check_response = requests.get(check_url)
    
      if check_response.status_code == 200:
        print("URL Confirmed Reachable!")
        url_dictionary[i] = 1
      else:
        print("Error Reaching URL")
        print("Error Received: " + str(check_response.status_code))
        url_dictionary[i] = 0
      
    if 0 in url_dictionary.values():
      print("Error reaching one or more URLs")
      status = 0
    else:
      print("All URLs Reachable!")
      status = 1
      
  else:
    print("Unable to load URL(s) to check")
  
  return status, url_list


def webscraper(URL):
  url_list = []
  input_type = check_input(URL)
  status, url_list = check_URL(URL, input_type)

  for url in url_list:
    i = url.strip()
    print("Scraping " + i + "...")
    basename = os.path.basename(i)
    output_file = "account_files/" + basename + "_emails.txt"
    print("Output File: " + output_file)
    _thread.start_new_thread(os.system, ("cewl " + i + "/ -n -d 2 -e --email_file " + output_file,))
    #os.system("cewl " + i + "/ -n -d 2 -e --email_file " + output_file)
    time.sleep(10)
    print("Waiting on scrape to complete...")
    count = 0
    while count < 20:
      time.sleep(15)
      if (os.stat(output_file).st_size > 1):
        print("Scrape complete!")
        break
      count += 1
    if count >= 20:
      print("Error: No emails found on target URL")
    print("Scraped " + i + " !")

  return
    





