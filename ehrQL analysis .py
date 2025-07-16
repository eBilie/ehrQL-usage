#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
import pandas as pd
import time 
import re 

token = 'my token'

headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github+json"
}

query = "ehrQL+language:python + org:opensafely" #Searching for code files that contain ehrQL, are written in python and belong to the OpenSafely org  
url = f"https://api.github.com/search/code"      

response = requests.get(url, headers=headers)

data = response.json()

 
per_page = 100 #pagination: upto 100 results per page as per GitHub allowance 
max_pages = 5  
all_results = []


for page in range(1, max_pages + 1):
    print(f"Searching GitHub - Page {page}")
    
    url = f"{url}?q={query}&per_page={per_page}&page={page}"
    response = requests.get(url, headers=headers)

    
    results = response.json().get("items", [])
    
   
    if not results:
        print("No more results.")
        break

    
    for item in results:
        file_url = item["html_url"]
        raw_url = file_url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")

        all_results.append({
            "File_Name": item["name"],
            "File_Path": item["path"],
            "Repository": item["repository"]["full_name"],
            "File_URL": file_url,
            "Raw_URL": raw_url
        })

    
    time.sleep(1) #considering GitHub's rate limits 



# In[2]:


df = pd.DataFrame(all_results)

df.to_csv("opensafely_ehrql_results.xlsx", index=False)

print("Results saved")


# In[3]:


df.shape


# In[5]:


df


# In[7]:


#Searching and Counting Specific EhrQL Functions Used in the Files Extracted

features_to_search = [
    r'show\(\)',               
    r'configure_dummy_data',  
    r'add_column'             
]

feature_counts = {   #To keep track of how many times each feature appears
    "show()": 0,
    "configure_dummy_data": 0,
    "add_column": 0
}


for index, row in df.iterrows(): #loop through each file 
    
    raw_url = row['Raw_URL']

    try:
       
        response = requests.get(raw_url)

        
        if response.status_code == 200:
            
            file_content = response.text

            
            for feature in features_to_search:
                count = len(re.findall(feature, file_content)) #check inside each file to count functions 
                
                
                if feature == r'show\(\)':
                    feature_counts["show()"] += count
                elif feature == r'configure_dummy_data':
                    feature_counts["configure_dummy_data"] += count 
                elif feature == r'add_column':
                    feature_counts["add_column"] += count
        else:
            print("NA", raw_url)

    except Exception as e:               #Used this to prevent any interuption incase of call failures 
        print("Error while", raw_url)
        print("   Reason:", e)

    
    time.sleep(0.5)


print("Total Count of Each Feature:") #Display count result 

for feature, total in feature_counts.items():
    print(f"{feature}: {total}")

