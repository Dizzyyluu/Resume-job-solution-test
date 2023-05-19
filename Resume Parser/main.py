import streamlit as st
import nltk
import requests
nltk.download('stopwords')
from pyresparser import ResumeParser
import os 
from apikey import apikey 
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain
from langchain.memory import ConversationBufferMemory

os.environ['OPENAI_API_KEY'] = apikey

# Define the Streamlit app
def get_job_recommendations(search_terms, location):
    url = "https://linkedin-jobs-search.p.rapidapi.com/"
    
    payload = {
        "search_terms": search_terms,
        "location": location,
        "page": "1"
    }
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": "92615d0181msha811bb2715cb4f8p1ebf71jsn697057e33940",
        "X-RapidAPI-Host": "linkedin-jobs-search.p.rapidapi.com"
    }
    
    response = requests.post(url, json=payload, headers=headers)
    job_results = response.json()
    
    return job_results

# Define the Streamlit app
def app():
    st.title('Resume Parser')
    first_name = st.text_input('First Name')
    last_name = st.text_input('Last Name')
    uploaded_file = st.file_uploader("Hi! Upload your resume file in PDF format", type=['pdf'])

    if uploaded_file is not None:
        # Parse the resume file
        resume_data = ResumeParser(uploaded_file).get_extracted_data()

        # Display the extracted details
        st.header("**Resume Info**")
        if resume_data.get('name'):
            st.success("Hello "+ first_name + ' ' + last_name)
            st.subheader("**Your Basic info**")
            try:
                st.write('Name: '+ first_name + ' ' + last_name)
                st.write('Email: ' + resume_data['email'])
                st.write('Contact: ' + resume_data['mobile_number'])
                st.text('Resume pages: ' + str(resume_data['no_of_pages']))
            except:
                pass
        else:
            st.error("Sorry, could not extract basic info from the resume")

        # Extract the skills
        skills = resume_data.get('skills', [])
        if skills:
            st.subheader("**Skills**")
            st.write(', '.join(skills))

        # Extract the work experience
        work_experience = resume_data.get('experience', [])
        if work_experience:
            st.subheader("**Work Experience**")
            for i, exp in enumerate(work_experience):
                if isinstance(exp, dict):
                    st.write(f"{i+1}. {exp.get('company', '')}: {exp.get('title', '')}: {exp.get('date_range', '')}")
                    st.write(f"   {exp.get('description', '')}")
                else:
                    st.write(f"{i+1}. {exp}")

        # Extract the education
        education = resume_data.get('education', [])
        if education:
            st.subheader("**Education**")
            for edu in education:
                st.write(edu['degree'] + ', ' + edu['major'] + ', ' + edu['date_range'])

        # Template for recommending jobs based on the skills and work_experience
        
        recommendation_template = PromptTemplate(
        input_variables = ['skills'], 
        template= "Given the following resume information: {skills}, recommend suitable jobs that qualifies me with job listings available and provide me with links to apply."
        )

        # Memory 
        #skills_memory = ConversationBufferMemory(input_key='resume_data', memory_key='chat_history')


        #llms

        llm = OpenAI(temperature=0.2) 
        recommendation_chain = LLMChain(llm=llm, prompt=recommendation_template, verbose=True, output_key='job')

        job = recommendation_chain.run(skills)


        st.subheader("**Recommended Job roles and links **")
        st.write(job) 

        #Pass extracted details to LinkedIn Jobs Search API
        job_search_query = ' '.join(skills)
        location = "Chicago, IL" 
        job_results = get_job_recommendations(job_search_query, location)

        # Display the job recommendations

        st.write("Debug: Job Results =", job_results)

        if job_results and 'data' in job_results:
            st.subheader("**Matching Jobs**")
            for i, job in enumerate(job_results['data']):
                st.write(f"{i+1}. {job['title']}")
                st.write(f"   {job['link']}")
        else:
            st.error("No matching jobs found.")

    else:
        st.write('Please upload a resume file')

if __name__ == '__main__':
    app()








