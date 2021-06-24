# HIBP API Integration

import os
import sys
import requests
import json
import time
import datetime
import argparse
import re


# Open HIBP API Key file and read in API Key value 
def get_api_key(api_file):
  g = open(api_file,"r")
  api_key = g.readline().strip()

  #try:
    #g = open(api_file,"r")
    #api_key = g.readline().strip()
  
  #except IOError:
    #print("Error opening HIBP API Key File")
    #exit()
  
  return api_key

# Deprecated now that webscraper outputs an account dict
def get_accounts():
  account_dict = {}
  
  if os.path.isdir("account_files"):
    filenames = os.listdir("account_files")
  else:
    print("Error getting account files -- is there an account_files directory?")
    filenames = 0
    exit()
  
  for i in filenames:
    accounts = []

    try:
      h = open("account_files/" + i, "r")

    except IOError:
      print("Error opening Accounts File")
      exit()

    else:
      print("Unknown Error")
      exit()

    for line in h:
      accounts.append(line.strip())
  
    # Update master dict with list of accounts for URL
    account_dict[i] = accounts
  
  return account_dict


def submit_account_breaches(account, api_key_file):
  
  # Set up payload with our HIBP API key and distinctive UAS
  req_headers = {'hibp-api-key': get_api_key(api_key_file),
             'user-agent': 'Hookshot'
            }

  # Set URL for account breaches
  breach_url = 'https://haveibeenpwned.com/api/v3/breachedaccount/' + account

  # Submit our GET request
  print("Submitting breach request for account: " + account)
  breaches_response = requests.get(breach_url, headers=req_headers)
  
  return breaches_response 
 
  
def submit_account_pastes(account, api_key_file):
  
  # Set up payload with our HIBP API key and distinctive UAS
  req_headers = {'hibp-api-key': get_api_key(api_key_file),
             'user-agent': 'Hookshot'
            }
  
  # Set URL for account pastes
  paste_url = 'https://haveibeenpwned.com/api/v3/pasteaccount/' + account
  
  # Submit our GET request
  print("Submitting paste request for account: " + account)
  pastes_response = requests.get(paste_url, headers=req_headers)
  
  return pastes_response


def check_account_breaches(breach_response, account):
  
  r = breach_response
  
  breach_info = {
    'num_breaches': 0,
    'breaches': []
  }
  
  # Checking for breaches 
  if r.status_code == 404:
    print("%s not found in a breach." %account)
    
  elif r.status_code == 200:
    data = r.json()
    print('----:Breach Found for: %s' %account)
    num_breaches = len(data)
    breach_info['num_breaches'] = num_breaches

  else:
    data = r.json()
    print('Error: <%s>  %s'%(str(r.status_code),data['message']))
    exit()

  return breach_info


def check_account_pastes(paste_response, account):
  
  r = paste_response
  
  paste_info = {
    'num_pastes': 0,
    'pastes': []
  }
  
  # Checking for pastes 
  if r.status_code == 404:
    print("%s not found in a paste." %account)
    
  elif r.status_code == 200:
    data = r.json()
    print('----:Paste Found for: %s' %account)
    num_pastes = len(data)
    paste_info['num_pastes'] = num_pastes

  else:
    data = r.json()
    print('Error: <%s>  %s'%(str(r.status_code),data['message']))
    exit()

  return paste_info


def hibp_checker(keyfile, account_dict):

  # Create nested dictionary
  output_dict = {}
  
  # Get accounts - not needed after adding the nested dict output to the webscraper
  #account_dict = get_accounts()
  
  # Submit each account for pastes and breaches
  for url, accounts in account_dict.items():

     # Set up logfile
    logfile = "hibp_output.log"
    output_file = open(logfile,"a+")
    
    # Create nested dict as key
    for account in accounts:

      # Double-check on email formatting
      regexp = re.compile(r'[a-zA-Z]+[\w.]*@[\w]*.[a-zA-Z]{3}')
      if regexp.search(str(account)):
        match_account = regexp.search(str(account)).group(1)

        # Add to nested dict
        output_dict[account] = {}
      
        # Submit account for breaches and check
        time.sleep(1)
        breach_result = submit_account_breaches(match_account, keyfile)
        breach_info = check_account_breaches(breach_result, match_account)

        # Submit account for pastes and check
        time.sleep(2)
        paste_result = submit_account_pastes(match_account, keyfile)
        paste_info = check_account_pastes(paste_result, match_account)
        time.sleep(1)

        # Output breach and paste info to nested dict
        output_dict[account]['URL'] = url.strip()
        output_dict[account]['Breach_Count'] = breach_info['num_breaches']
        output_dict[account]['Breach_Detail'] = breach_info['breaches']
        output_dict[account]['Paste_Count'] = paste_info['num_pastes']
        output_dict[account]['Paste_Info'] = paste_info['pastes']
      
    # Close output file
    output_file.close()
  return output_dict


