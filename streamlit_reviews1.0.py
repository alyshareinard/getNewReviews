import os
import streamlit as st


api_key = st.secrets["api_key"]

import pandas as pd
from pyairtable.formulas import match

from pyairtable import Api, Base, Table


def get_reviews(reviewerRecord):
    get_more=False
    st.write("Getting companies.  This will take a minute... ")
    reviewerGender = reviewerRecord['fields']['Gender'].lower()
    batch_size = 10
    dailyLimit = reviewerRecord['fields']['daily limit']
    monthlylimit = reviewerRecord['fields']['monthly limit']
    doneToday = reviewerRecord['fields']['# Reviews today']
    doneThisMonth = reviewerRecord['fields']['# Reviews this month']
    if reviewerGender == "female":
        genderToAvoid = "male"
    elif reviewerGender == "male":
        genderToAvoid = "female"
    else:
        genderToAvoid = "none"
    revCount=0
    goodCompanies=[]
    companyNames=[]
    companyUrls = []
    productUrls = []
    wherefromUrls=[]
    companySizes=[]
    brandProduct = []
    done=False
    #here we step through the company list in batches of 100 looking for non-matching companies
    for companies in company_table.iterate(view='Priority', page_size=100):
        if done: 
            break
        for companyRecord in companies:
#                    print(company['id'])
            company_id=companyRecord['id']
            company=companyRecord['fields']
            if 'Gender needed' in company.keys():
                genderNeeded = company['Gender needed'].lower()
            else:
                genderNeeded = "anything"
#                    print(genderNeeded)
            #print(companiesDone)
            if (company['seoName'] not in companiesDone and genderNeeded!=genderToAvoid) and 'Company name' in company.keys():
#                        print(company['fields']['Company name'])
                print(company.keys())
                companyNames.append(company['Company name'])
                companiesDone.append(company['seoName'])

                if 'Product URL' in company.keys():
                    productUrls.append(company['Product URL'])
                else:
                    productUrls.append("")

                if 'Wherefrom company url' in company.keys():
                    wherefromUrls.append(company['Wherefrom company url'])
                else:
                    wherefromUrls.append("")

                if 'size' in company.keys():
                    companySizes.append(company['size'])
                else:
                    companySizes.append("")

                if 'URL' in company.keys():
                    companyUrls.append(company['URL'])
                else:
                    companyUrls.append("")


                if 'Brand or Product' in company.keys():
                    brandProduct.append(company['Brand or Product'])
                else:
                    brandProduct.append("")

                revCount+=1
                if "Reviews done this week" in company:
                    companyCount = company["Reviews done this week"]+1
                else:
                    companyCount=1
                researchers_table.update(reviewerRecord['id'], {"reviewed seos":"['" + "', '".join(companiesDone)+"']", "# Reviews today":reviewerRecord["fields"]["# Reviews today"]+revCount, "# Reviews this month":reviewerRecord["fields"]["# Reviews this month"]+revCount})#, "Companies reviewed":"[" + ", ".join(linked_companies)+"]"})
                company_table.update(company_id, {"Reviews done this week":companyCount})

                if revCount>=batch_size or doneToday+revCount>=dailyLimit or doneThisMonth+revCount>=monthlylimit:
                    response_df = pd.DataFrame({"Company":companyNames, "Brand or Product":brandProduct, "Company URL":companyUrls, "Product URL":productUrls, "Wherefrom URL":wherefromUrls, "Size":companySizes})

                    pd.set_option('display.max_colwidth', -1)
                    st.markdown(response_df.to_html(render_links=True),unsafe_allow_html=True)
                    done=True
                    break

#    more_reviews_button = st.button("Done with this set?", key="more_reviews")


def make_clickable(link):
    # target _blank to open new window
    # extract clickable text to display for your link
#    text = link.split('=')[1]
    return f'<a target="_blank" href="{link}">{link}</a>'


def color_products(s):
    if s["Brand or Product"]=="Product":
        return ['background-color: grey']*len(s)
    else:
        return ['background-color: black']*len(s)

def process_dups():
    print('in callback')
    print(st.session_state.data.data.keys()) 
    print(st.session_state.data)

if 'load_state' not in st.session_state:
    st.session_state.load_state = False

if 'time_to_process' not in st.session_state:
    st.session_state['time_to_process'] = False

if 'dups' not in st.session_state:
    st.session_state['dups'] = False

if 'data' not in st.session_state:
    st.session_state['data'] = []

if 'more_reviews' not in st.session_state:
    st.session_state['more_reviews'] = False

researchers_table = Table(api_key, 'appXAmOdVlbrsjpKm', 'tblTqaq5Xtwlin7Vj')
company_table = Table(api_key, 'appXAmOdVlbrsjpKm', 'tbl92zocl5cINJnyg')


st.title("Get new brands to review.")
get_more=False

email = st.text_input("Email", disabled=False).strip()
if email: 
    print(email)
    st.write('Getting record...')
    res_formula = match({'email':email})
    reviewerRecord = researchers_table.first(formula=res_formula)
    maxReviews = 10
    if reviewerRecord:
        st.write('Welcome ', reviewerRecord['fields']['Researcher name'])
        st.write("Reviews today: ", reviewerRecord['fields']['# Reviews today'])
        st.write("Reviews this month: ", reviewerRecord['fields']['# Reviews this month'])
        if 'reviewed seos' in reviewerRecord['fields']:
            companiesDone = eval(reviewerRecord['fields']['reviewed seos'])

        else:
            companiesDone=[]

        if reviewerRecord['fields']["Available for reviews"]=="False":

            st.write("Sorry, you've done your limit for now.")
            print("at limit")
        else:
            time_to_process_button = st.button("Request reviews", key="time_to_process")
    else:
        st.write("Reviewer not found -- enter email again")

if st.session_state.time_to_process or get_more==True:
    get_reviews(reviewerRecord)
