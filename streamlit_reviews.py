import os
import streamlit as st
from datetime import datetime, date

api_key = st.secrets["api_key"]

import pandas as pd
from pyairtable.formulas import match
from pyairtable import Api, Base, Table

def get_previous(email):
    st.write("Accessing database...")
    print(email)
    rev_formula = match({'reviewer email':email})
    reviews = pd.DataFrame(reviews_table.all(formula=rev_formula, sort=["-date"]))
    reviews = reviews['fields']
    companyURL=[]
    productURL=[]
    wherefromURL=[]
    date=[]
    for review in reviews:
        print(review)
        if 'company URL' in review:
            companyURL.append(review['company URL'])
        else:
            companyURL.append("")
        if 'product URL' in review:
            productURL.append(review['product URL'])
        else:
            productURL.append("")
        if 'wherefrom URL' in review:
            wherefromURL.append(review['wherefrom URL'])
        else:
            wherefromURL.append("")
        if 'date' in review:
            date.append(review['date'])
        else:
            date.append("")

#    reviews = pd.DataFrame(reviews['fields'])
    print(companyURL)
    print(len(reviews))
    response_df = pd.DataFrame({"Company URL":companyURL, "Product URL":productURL, "Wherefrom URL":wherefromURL, "Date":date})
    response_df.index = response_df.index + 1                    
    pd.set_option('display.max_colwidth', None)
    st.markdown(response_df.to_html(render_links=True),unsafe_allow_html=True)

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
            #  print(company.keys())
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
                reviews_table.create({'reviewer email':reviewerRecord['fields']['Email'], 'seoname': company['seoName'], 'product URL':productUrls[-1], 'company URL':companyUrls[-1], 'wherefrom URL':wherefromUrls[-1]})


                if revCount>=batch_size or doneToday+revCount>=dailyLimit or doneThisMonth+revCount>=monthlylimit:
                    response_df = pd.DataFrame({"Company":companyNames, "Brand or Product":brandProduct, "Company URL":companyUrls, "Product URL":productUrls, "Wherefrom URL":wherefromUrls, "Size":companySizes})
                    response_df.index = response_df.index + 1                    
                    pd.set_option('display.max_colwidth', None)
                    st.markdown(response_df.to_html(render_links=True),unsafe_allow_html=True)
                    
                    done=True
                    if doneToday+revCount>=dailyLimit or doneThisMonth+revCount>=monthlylimit:
                        reviewerRecord['fields']["Available for reviews"]=0
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



if 'load_state' not in st.session_state:
    st.session_state.load_state = False

if 'dups' not in st.session_state:
    st.session_state['dups'] = False

if 'data' not in st.session_state:
    st.session_state['data'] = []

if 'more_reviews' not in st.session_state:
    st.session_state['more_reviews'] = False

researchers_table = Table(api_key, 'appXAmOdVlbrsjpKm', 'tblTqaq5Xtwlin7Vj')
company_table = Table(api_key, 'appXAmOdVlbrsjpKm', 'tbl92zocl5cINJnyg')
reviews_table = Table(api_key, 'appXAmOdVlbrsjpKm', 'tblxayMvcreRucnK2')

st.title("Get new brands to review.")
get_more=False

email = st.text_input("Email", disabled=False).strip()
if email: 
#    print(email)
    st.write('Getting record...')
    res_formula = match({'email':email})
    reviewerRecord = researchers_table.first(formula=res_formula)
    maxReviews = 10
    if reviewerRecord:
        if "Last Modified" in reviewerRecord['fields']:
            last_modified = datetime.strptime(reviewerRecord['fields']['Last Modified'], '%Y-%m-%dT%H:%M:%S.%fZ')
            print(date.today())
            print(last_modified.date())
            if last_modified.date()<date.today():
                reviewerRecord['fields']['# Reviews today'] = 0
                if last_modified.month<date.today().month:
                    reviewerRecord['fields']['# Reviews this month'] = 0
                if reviewerRecord['fields']['# Reviews this month']<reviewerRecord['fields']['monthly limit']:
                    reviewerRecord['fields']['Available for reviews']=1
                if reviewerRecord['fields']['# Reviews today']<reviewerRecord['fields']['daily limit']:
                    reviewerRecord['fields']['Available for reviews']=1
        if 'Researcher name' in reviewerRecord['fields']:
            st.write('Welcome ', reviewerRecord['fields']['Researcher name'])
        else:
            st.write('Welcome')
        st.write("Reviews today: ", reviewerRecord['fields']['# Reviews today'])
        st.write("Reviews this month: ", reviewerRecord['fields']['# Reviews this month'])
        if 'reviewed seos' in reviewerRecord['fields']:
            companiesDone = eval(reviewerRecord['fields']['reviewed seos'])

        else:
            companiesDone=[]

        if reviewerRecord['fields']["Available for reviews"]==0:

            st.write("Sorry, you've done your limit for now.")
#            print("at limit")
        else:
            time_to_process = st.button("Request reviews")
            get_recent_reviews = st.button("See recent assigned companies")
            if time_to_process and reviewerRecord['fields']["Available for reviews"]==1:
                get_reviews(reviewerRecord)
            if get_recent_reviews:
                get_previous(email)

    else:
        st.write("Reviewer not found -- enter email again")


