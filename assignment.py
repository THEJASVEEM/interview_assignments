import json
from sseclient import SSEClient as EventSource
import schedule

#Variables declared
minute = 0
url = 'https://stream.wikimedia.org/v2/stream/revision-create'
five_min_list_domain = []
five_min_list_title = []
five_min_list_user = []
dict_domain_min = {}
dict_page_title_min = {}
dict_users_min ={}
dict_domain_5min = {}
dict_page_title_5min = {}
dict_users_5min ={}

#Function to display the report every minute
def DisplayOneMinReprt():
    #print the minute
    global minute
    minute +=1
    print("\nMinute ", minute," Report\n")

    #append the last min data to the list
    five_min_list_domain.append(dict_domain_min)
    five_min_list_title.append(dict_page_title_min)
    five_min_list_user.append(dict_users_min)

    #remove previous data if its been more than 5 min
    if(len(five_min_list_domain)>5):
        del five_min_list_domain[0]
        
    if(len(five_min_list_title)>5):
        del five_min_list_title[0]
    
    if len(five_min_list_user)>5:
        del five_min_list_user[0]

    #merge the data into one dictionary
    for i in five_min_list_domain:
        for key, val in i.items():
            dict_domain_5min[key] = dict_domain_5min.get(key, 0) + val
            
    print("\nTotal number of Wikipedia Domains Updated: ", len(dict_domain_5min), "\n")

    for i in five_min_list_title:
        dict_page_title_5min.update(i)
        # for key, val in i.items():
        #     dict_page_title_5min[key] = dict_page_title_5min.get(key, 0) + val
    
    for i in five_min_list_user:
        dict_users_5min.update(i)
        # for key, val in i.items():
        #     dict_users_5min[key] = dict_users_5min.get(key, 0) + val
    
    #sort and print the domain report
    sort_dict_domain=dict(sorted(dict_domain_5min.items(), key=lambda item: item[1], reverse=True))
    for key, val in sort_dict_domain.items():
        if val > 1:
            print(key, ':', val, "Pages updated")
        else:
            print(key, ':', val, "Page updated")
    
    print("\nUsers who made changes to en.wikipedia.org ", len(dict_users_5min),"\n")

    #sort and print the domain report
    sort_dict_user=dict(sorted(dict_users_5min.items(), key=lambda item: item[1], reverse=True))
    for key, val in sort_dict_user.items():
        print(key, ':', val)

    #clear the dictionaries for next min data
    dict_domain_min.clear()
    dict_page_title_min.clear()
    dict_users_min.clear()
    dict_domain_5min.clear()
    dict_page_title_5min.clear()
    dict_users_5min.clear()



#scheduler for every 60 min
schedule.every(60).seconds.do(DisplayOneMinReprt)


#for loop for picking data continuosly from API
for event in EventSource(url):
    if event.event == 'message':
        try:
            change = json.loads(event.data)
        except ValueError:
            pass
        else:
                #One min users report adding to dictionary
            if change['performer']['user_is_bot']==False and change.get('performer').get('user_edit_count'):
                dict_users_min[change['performer']['user_text']] = change['performer']['user_edit_count']

                #One Min domain report adding to a dictionary 
                #checking for uniquely editted page
            if change['page_title'] in dict_page_title_min:
                continue
            else:
                dict_page_title_min[change['page_title']] = dict_page_title_min.get(change['page_title'], 0) + 1
                dict_domain_min[change['meta']['domain']] = dict_domain_min.get(change['meta']['domain'], 0) + 1
            schedule.run_pending()