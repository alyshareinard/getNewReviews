import os
import streamlit as st


api_key = st.secrets["api_key"]
import pandas as pd
from pyairtable.formulas import match

from pyairtable import Api, Base, Table


def get_reviews():
    get_more=False
    st.write("Getting companies... ")
    reviewerGender = reviewerRecord['fields']['Gender'].lower()
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

    #here we step through the company list in batches of 100 looking for non-matching companies
    for companies in company_table.iterate(view='Priority', page_size=100):
        if revCount>=maxReviews: 
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
            if (company['seoName'] not in companiesDone and genderNeeded!=genderToAvoid) and 'Company name' in company.keys():
#                        print(company['fields']['Company name'])
#                            print(company.keys())
                companyNames.append(company['Company name'])

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


                    
                reviews_table.create({'Researcher':[reviewerRecord['id']], 'Company (seo)': [company_id], 'uploaded':False})
                revCount+=1
                companiesDone.append(company['seoName'])
#                            print("adding ", company['seoName'], company_id)

                if revCount>=maxReviews:
                    response_df = pd.DataFrame({"Company":companyNames, "Brand or Product":brandProduct, "Company URL":companyUrls, "Product URL":productUrls, "Wherefrom URL":wherefromUrls, "Size":companySizes})

                    #response_df.style.apply(color_products, axis=None)
                    #response_df['Company URL'] = response_df['Company URL'].apply(make_clickable)
                    #response_df = response_df.to_html(escape=False)
                    pd.set_option('display.max_colwidth', -1)
                    st.markdown(response_df.to_html(render_links=True),unsafe_allow_html=True)
#                    st.dataframe(response_df)
                    

    #                            print("all done!")
                    break
#    dups_button = st.button("Report Duplicates")#, on_click=process_dups())
    more_reviews_button = st.button("Done with this set?", key="more_reviews")
#    if dups_button:
#        dups = st.text_input("enter duplicates here")
#        print(dups)

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

reviews_table = Table(api_key, 'appDLr6e0UiouhRNJ', 'tblpkHZYmtEhEiMCf')
researchers_table = Table(api_key, 'appDLr6e0UiouhRNJ', 'tblzBfI622DiklzYG')
company_table = Table(api_key, 'appDLr6e0UiouhRNJ', 'tblPdEGdqEjFPHPBD')

st.title("Get new brands to review")
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
        if 'seo rollup' in reviewerRecord['fields']:
            companiesDone = eval(reviewerRecord['fields']['seo rollup'])
        else:
            companiesDone=[]

        print("Num companies already done ", len(companiesDone))
#        if reviewerRecord['fields']["Available for reviews"]=="False":
        limit=False
        if limit==True:
            st.write("Sorry, you've done your limit for now.")
            print("at limit")
        else:
            time_to_process_button = st.button("Request reviews", key="time_to_process")
    else:
        st.write("Reviewer not found -- enter email again")
if st.session_state.time_to_process or get_more==True:
    get_reviews()
    if st.session_state.dups:
        print("We're in dups!")
        print(st.session_state.data.data.keys()) 
        print(st.session_state.data)
    #    for dup in st.stession_state.dups:
            

    if st.session_state.more_reviews:
        print("setting get_more")
        get_more=True

