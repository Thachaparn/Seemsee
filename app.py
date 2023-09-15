import streamlit as st
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chains import SequentialChain
from random import randint  
# set page title and favicon.
st.title('🔮 :violet[แม่หมออ้อย-ฉอด]')
st.subheader("*บริการปรึกษาปัญหาใจ คลายทุกข์ผ่าน :red[บทกลอน]*")

# add a text input box for the user to enter their OpenAI API key.
openai_api_key = st.sidebar.text_input('OpenAI API Key', type='password')

# Define a function to authenticate to OpenAI API with the user's key, send a prompt, and get an AI-generated response.
# def generate_response(input_text):
#     llm = OpenAI(temperature=0.7, openai_api_key=openai_api_key)
#     # Accepts the user's prompt as an argument and displays the AI-generated response in a blue box 
#     st.info(llm(input_text))

def build_sequential_llm():
    # This is an LLMChain to write a synopsis given a title of a play and the era it is set in.
    counselor_llm = OpenAI(temperature=.7, openai_api_key=openai_api_key)
    counselor_template = """You are a counselor. Given the issue and counseling style from a client, it is your job to write a suggestion on how to deal with their issues in the counseling style that fits him.
    

    issue: {issue}
    style: {style}
    Counselor gives a suggestion here:"""
    counselor_prompt_template = PromptTemplate(input_variables=["issue", "style"], template=counselor_template)
    counselor_chain = LLMChain(llm=counselor_llm, prompt=counselor_prompt_template, output_key="suggestion")

    

    # This is an LLMChain to write a review of a play given a synopsis.
    poet_llm = OpenAI(temperature=.7, openai_api_key=openai_api_key)
    template = """You are a poet. Given the suggestion from the counselor, it is your job to write a poem based on the suggestion.

    Suggestion:
    {suggestion}
    A poem based on the suggestion from counselor:"""
    prompt_template = PromptTemplate(input_variables=["suggestion"], template=template)
    poet_chain = LLMChain(llm=poet_llm, prompt=prompt_template, output_key="poem")
    
    st.toast('แม่หมอเห็นบางอย่าง...🤩')

    overall_chain = SequentialChain(chains=[counselor_chain, poet_chain],
                                    input_variables=["issue", "style"],
                                    output_variables=["suggestion", "poem"], 
                                    verbose=False)
    return overall_chain

# Add a form to the page.
with st.form('my_form'):
    # Add a text area for the user to enter their prompt.
    issue = st.text_area('ไม่สบายใจอะไร ไหนเล่าให้แม่หมอฟังซิ:', 'อยากจะขอคำแนะนำเรื่อง...')

    style = st.radio('อยากให้แม่หมอพูดตรง ๆ หรือเปล่าคะ?',
                     ["gentle", "harsh"],
                     captions = ["เบา ๆ แม่ ใจคนเรามันบาง", "ขอแรง ๆ จัดมาได้เลยแม่"])
    
    input_dict = {"issue":issue, "style": style}

    st.info("หลับตา ตั้งจิตอธิษฐานแล้วกดปุ่มเขย่าเซียมซี")
    # Add a submit button.
    submitted = st.form_submit_button('เขย่าเซียมซี!', type='primary')
    # If the user has not entered their OpenAI API key, display a warning.
    if not openai_api_key.startswith('sk-'):
        st.warning('Please enter your OpenAI API key!', icon='⚠')
    # If the user has entered their OpenAI API key and submitted the form, call the generate_response function.
    if submitted and openai_api_key.startswith('sk-'):
        with st.spinner('แม่หมอกำลังทำนาย...'):
            all_chain = build_sequential_llm()
            result = all_chain(input_dict)
            st.toast('ผลการทำนายมาแล้ว...🎴')

        st.balloons()
        
        try:
            st.subheader('คำทำนายหมายเลข '+':red[{}]'.format(randint(1,20)), divider='violet')
            st.caption("แม่หมอแนะนำว่า ... ")
            poem = result['poem']
            st.info(poem)
 
            with st.expander("อยากให้แม่หมออธิบายให้ฟังง่ายๆ กดที่นี่เลย 👇🏻"):
                suggestion = result['suggestion']
                st.write(suggestion)
        except Exception as e:
            st.error("Something went wrong!:\n{}".format(e))