import os
import streamlit as st

api_key = st.secrets["api_key"]
import pandas as pd
from pyairtable.formulas import match
import time
from pyairtable import Api, Base, Table


reviews_table = Table(api_key, 'appDLr6e0UiouhRNJ', 'tblpkHZYmtEhEiMCf')
researchers_table = Table(api_key, 'appDLr6e0UiouhRNJ', 'tblzBfI622DiklzYG')
company_table = Table(api_key, 'appDLr6e0UiouhRNJ', 'tblPdEGdqEjFPHPBD')

st.title("Get new brands to review")

email = st.text_input("Email", disabled=False).strip()
if email: 
    st.write('Getting record...')

    res_formula = match({'email':email})
    reviewerRecord = researchers_table.first(formula=res_formula)
    maxReviews = 10
    if reviewerRecord:
        st.write('Welcome ', reviewerRecord['fields']['Researcher name'])
        if 'seo rollup' in reviewerRecord['fields']:
            companiesDone = eval(reviewerRecord['fields']['seo rollup'])
        else:
            companiesDone=[]
        if reviewerRecord['fields']["Available for reviews"]=="False":
            st.write("Sorry, you've done your limit for now.")
            st.write("Reviews today: ", reviewerRecord['fields']['# Reviews today'])
            st.write("Reviews this month: ", reviewerRecord['fields']['# Reviews this month'])
        else:
            time_to_process = st.button("Request reviews")
            if time_to_process:
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
                        if (company['seoName'] not in companiesDone and genderNeeded!=genderToAvoid):
    #                        print(company['fields']['Company name'])
    #                        print(company['fields'].keys())
                            if 'Product URL' in company.keys():
                                st.write(company['Company name'], "    ", company['Product URL'])
                            else:
                                st.write(company['Company name'], "    ", company['Wherefrom company url'], company['size'])
                            reviews_table.create({'Researcher':[reviewerRecord['id']], 'Company (seo)': [company_id]})
                            revCount+=1
                            companiesDone.append(company['seoName'])

                            if revCount>=maxReviews:
    #                            print("all done!")
                                break
    #                    else:

    else:
        st.write("Reviewer not found -- enter email again")