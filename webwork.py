# Email Webscraper

import os
import signal
import sys
import requests
import json
import time
import subprocess
import datetime
import argparse
import re
import random


# Check our input (single URL or file) 
def check_input(url):
  if os.path.isfile(url):
    print("Loaded - URL List Mode\n")
    input_type = 2
  elif "http" or "www" or "://" in url:
    print("Loaded - Single URL Mode\n")
    input_type = 1
  else:
    print("URL Input Error\n")
    input_type = 0
    
  return input_type

# Check that we can reach the URL
def check_URL(URL, input_type):
  url_dict = {}
  if input_type == 1:
    time.sleep(1)
    print("Checking Single URL (" + URL + ")...")
    url_dict[URL] = 0
    check_response = requests.get(URL + "/")

    # Check our reponse and output the code we get for the URL
    if check_response.status_code == 200 or check_response.status_code == 403 or check_response.status_code == 406:
      print("Received Code " + str(check_response.status_code) + " -- Reachable!")
      url_dict[URL] = check_response.status_code
    else:
      print("Error Reaching URL -- Received Code " + str(check_response.status_code))
      url_dict[URL] = check_response.status_code

  elif input_type == 2:
    print("Checking list of URLs to reach...")
    with open(URL) as f:
      url_list = f.readlines()
      url_dict = { url.strip() : 0 for url in url_list }
    for c in url_list:
      i = c.strip()
      time.sleep(0.5)
      print("\nChecking " + i.strip() + "...")

      # Clean up the url
      check_url = i.strip()

      # Send our GET request with a Windows Firefox UAS (fixes a 406 error)
      check_response = requests.get(check_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"})

      if check_response.status_code == 200 or check_response.status_code == 403 or check_response.status_code == 406:
        print("Received Code " + str(check_response.status_code) + " -- Reachable!")
        url_dict[i] = check_response.status_code
      else:
        print("Error Reaching URL -- Received Code " + str(check_response.status_code))
        url_dict[i] = check_response.status_code
      
    if 404 in url_dict.values():
      print("Error reaching one or more URLs")
      status = 0
    else:
      print("\nAll " + str(len(url_list)) + " URLs Reachable!\n")
      time.sleep(1)
      status = 1
      
  else:
    print("Unable to load URL(s) to check")
  
  return url_dict

def webscraper(URL, depth, timeout):

  # Set up our list and dict
  output_dict = {}
  url_list = []
  
  # Check whether we received a single URL or a list
  input_type = check_input(URL)
  
  # Check all our URLs to make sure we can reach them 
  url_dict = check_URL(URL, input_type)
  url_list = url_dict.keys()

  # Set up process dict
  process_dict = {}

  # Run scrapes on target URLs
  for url in url_list:

    # Check URL formatting
    i = url.strip()
    print("\nScraping " + i + "...")

    time.sleep(1)

    # Set up request parameters
    url_new = i + "/"
    uas_list = [
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
      "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36",
      "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322)",
      "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)",
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
      "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134",
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/18.17763",
      "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; KTXN)"
    ]

    # Grab a random UAS from our list
    uas = random.choice(uas_list)

    # Use single UAS without randomly changing -- this one works pretty well on most sites
    #uas = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'

    # Run our scrapes in parallel -- best results with depth at 2 (faster) or 3 (longer, but more thorough)
    # Set up scrape command
    scrape_command = "cewl " + str(url_new) + " --ua '" + str(uas) + "' -n -d " + str(depth) + " -e " #--email_file " + str(output_file)

    # Run subprocess under our dict
    # Using ulimit and nice to control CPU usage and process timeout, default: ulimit -t 32400
    #process_dict[i] = subprocess.Popen("ulimit -t " + str(timeout) + "; " + str(scrape_command), stdout=subprocess.PIPE, shell=True)
    process_dict[i] = subprocess.Popen(str(scrape_command), stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
    # Optional -- add 'nice -n 15' for granular CPU usage control

    # Optional - run scrapes in series using wait()
    #process_dict[i].wait()
    time.sleep(1)

  # Adjust this wait time if you want more frequent status checking
  # Default 10 sec
  check_time = 10

  # Set up loop and variables
  proc_states = {}
  proc_complete = 0

  #Run loop until we need to timeout our subprocesses
  while proc_complete <= (timeout / check_time ):

    # Reset scrape count
    running_scrapes = 0

    for url in url_list:
      i = url.strip()

      # If proc is still running, add to count of running scrapes
      if process_dict[i].poll() is None:
        proc_states[i] = 0
        running_scrapes += 1

      # If the proc is done, clear it -- if it just finished, print status update
      else:

        if proc_states[i] != 1:
          print("Scrape on " + str(i) + " complete!")

        # Update in process dict
        proc_states[i] = 1

    # If we're still waiting on scrapes, output how many and sleep for a minute
    if 0 in proc_states.values():
      proc_complete += 1
      print("Waiting on " + str(running_scrapes) + " scrape(s) to complete...")
      time.sleep(check_time)

    else:
      proc_complete = (timeout / check_time )
      print("\nAll Scrapes Complete!\n")

  # Kill all of our subprocesses that are still running
  for url in url_list:

    # Check URL formatting
    i = url.strip()

    # Send sigterm to subprocess
    if proc_states[i] == 0:
      print("Killing timed-out scrape on " + str(i) )
      os.killpg(os.getpgid(process_dict[i].pid), signal.SIGTERM)

  # Set up output dictionary
  output_dict = {}
  
  # Grab output from subprocess module
  for url, process in process_dict.items():
    
    i = url.strip()

    # Get output from subprocess
    subproc_return = process.stdout.read()
    subproc_return = subproc_return.decode("utf-8")

    # Run regex against output, strip out only emails that match formatting
    regexp = re.compile(r'[a-zA-Z]+[\w.]*@[\w]*.[a-zA-Z]{3}')
    if regexp.search(subproc_return):
      output_dict[i] = regexp.findall(str(subproc_return))

    # If no match, throw a placeholder in for url
    if len(subproc_return) <= 75:
      output_dict[i] = ''

  return output_dict
