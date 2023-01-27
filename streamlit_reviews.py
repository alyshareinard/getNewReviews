import os
import streamlit as st

api_key = st.secrets["api_key"]
import pandas as pd
from pyairtable.formulas import match
import time
from pyairtable import Api, Base, Table

def upload_completed_reviews():
    reviews_table = Table(api_key, 'appDLr6e0UiouhRNJ', 'tblpkHZYmtEhEiMCf')
    researchers_table = Table(api_key, 'appDLr6e0UiouhRNJ', 'tblzBfI622DiklzYG')
    company_table = Table(api_key, 'appDLr6e0UiouhRNJ', 'tblPdEGdqEjFPHPBD')
    researchers = researchers_table.all()
    companies = company_table.all()
    reviews = reviews_table.all()
    #existing_reviews = reviews_table.all(fields = ['Name'])

    rev_emails = []
    rev_seos = []
    rev_names = []
    for review in reviews:
        fields = review['fields']
#        print("fields: ", fields)
        rev_emails.append(fields['email_lookup'])
        rev_seos.append(fields['seo_lookup)'])
        rev_names.append(fields['email_lookup']+'-'+fields['seo_lookup'])

    seoList = []
    for company in companies:
        fields = company['fields']
        try:
            seoList.append(fields['seoName'])
        except:
            print('append failed for: ', company)


    #reviewed_brands = pd.read_csv("./Reviewer-files/researchReviewsWithSeoName.csv", header=0).dropna(how='all')
    reviewed_brands = pd.read_csv("~/Downloads/researchers_reviews.csv", header=0).dropna(how='all')
    #print(reviewed_brands)
    nullcount=0

    for i in range(len(reviewed_brands)):
        offset = 53993
        print('i', i+offset)

        email = reviewed_brands.email[i + offset]
        brand = reviewed_brands[" seo_name "][i + offset].strip()
        reviewed_name = email + '-' + brand
        if reviewed_name not in rev_names:

            if brand not in (seoList):
                print('brand not in list', brand)
                continue

            formula = match({'Researcher':email, 'Company (seo)':brand})
            if brand=="NULL" or brand != brand or brand=="null":
                nullcount+=1
                ismatch=True #skip these ones
            else:
                ismatch = reviews_table.first(formula=formula)
            print("email ", email, " brand ", brand)
            print('.', end="")
            if ismatch:
                with open("inAirtable.txt", 'a') as f:
                    f.writelines(email + " " + brand + "\n")

            if not ismatch:
                #first find the researcher
                res_formula = match({'email':email})
                resmatch = researchers_table.first(formula=res_formula)
                if resmatch==None:
                    print("researcher doesn't exist, skipping", email)
    #                researchers_table.create({"Email":email})


                #find company
                comp_formula = match({'seoName':brand})
                compmatch = company_table.first(formula=comp_formula)
                
                if resmatch and compmatch:
                    time.sleep(0.5)

                    reviews_table.create({'Researcher':[resmatch['id']], 'Company (seo)': [compmatch['id']], 'uploaded':True})


    print(nullcount, "missing values")
            




reviews_table = Table(api_key, 'appDLr6e0UiouhRNJ', 'tblpkHZYmtEhEiMCf')
researchers_table = Table(api_key, 'appDLr6e0UiouhRNJ', 'tblzBfI622DiklzYG')
company_table = Table(api_key, 'appDLr6e0UiouhRNJ', 'tblPdEGdqEjFPHPBD')
#researchers = researchers_table.all()


st.title("Get new brands to review")


email = st.text_input("Email", disabled=False)
if email: 
    st.write('Getting record...')

    res_formula = match({'email':email})
    reviewerRecord = researchers_table.first(formula=res_formula)

    if reviewerRecord:
        st.write('Welcome ', reviewerRecord['fields']['Researcher name'])
        companiesDone = eval(reviewerRecord['fields']['seo rollup'])
        
        time_to_process = st.button("Request reviews")
        if time_to_process:
            st.write("Searching... ")
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
                if revCount>33: 
                    break
                for companyRecord in companies:
#                    print(company['id'])
                    company_id=companyRecord['id']
                    company=companyRecord['fields']
                    if 'Gender needed' in company.keys():
                        genderNeeded = company['Gender needed'].lower()
                    else:
                        genderNeeded = "anything"
                    print(genderNeeded)
                    if (company['seoName'] not in companiesDone and genderNeeded!=genderToAvoid):
#                        print(company['fields']['Company name'])
#                        print(company['fields'].keys())
                        if 'Product URL' in company.keys():
                            st.write(company['Company name'], "    ", company['Product URL'])
                        else:
                            st.write(company['Company name'], "    ", company['Wherefrom company url'], company['size'])
                        reviews_table.create({'Researcher':[reviewerRecord['id']], 'Company (seo)': [company_id], 'uploaded':True})
                        revCount+=1
                        companiesDone.append(company['seoName'])

                        if revCount>33:
                            print("all done!")
                            break
                    else:
                        print("skipping ", company['seoName'])




#        companies = company_table.all(view='Priority')
#        reviews = reviews_table.all()


    #     noContactsFound = list(set(seolist) - set(output_file['seoName']))
    #     print(noContactsFound)
    #     st.write("No contacts found for these seoNames: ", noContactsFound)
    #     # except Exception as e:
    #     #     st.write("Error\n", e)
    #     #     output_file=[]

    #     if len(output_file)>0:
    #         @st.cache
    #         def convert_df(df):
    #             # IMPORTANT: Cache the conversion to prevent computation on every rerun
    #             return df.to_csv().encode('utf-8')

    #         csv = convert_df(output_file)

    #         st.download_button(
    #             label="Download data as CSV",
    #             data=csv,
    #             file_name='companies_to_review.csv',
    #             mime='text/csv',
    #         )
    else:
        st.write("Reviewer not found -- enter email again")