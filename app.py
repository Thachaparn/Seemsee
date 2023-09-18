import streamlit as st
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chains import SequentialChain
from langchain.chat_models import ChatOpenAI
from random import randint
import datetime

# Get the current date
current_date = datetime.datetime.now().date()

# Define the date after which the model should be set to "gpt-3.5-turbo"
target_date = datetime.date(2024, 6, 12)

# Set the model variable based on the current date
if current_date > target_date:
    llm_model = "gpt-3.5-turbo"
else:
    llm_model = "gpt-3.5-turbo-0301"

def build_sequential_llm():
    # detect language
    llm = ChatOpenAI(temperature=.7, openai_api_key=openai_api_key, model=llm_model)
    template_lang = """Detect the language in the given issue.

    issue:
    {issue}

    lang:
    """

    lang_prompt_template = PromptTemplate(input_variables=["issue"], template=template_lang)
    lang_chain = LLMChain(llm=llm, prompt=lang_prompt_template, output_key="lang")
    
    st.toast('กำลังตรวจสอบภาษา...🔍')

    # get suggestion
    template_cons = """You are a counselor. Give a concise suggestion on how to deal with the issue in {lang}. Be {style} as much as possible.

    issue:
    {issue}
    """
    cons_prompt_template = PromptTemplate(input_variables=["issue", "style", "lang"], template=template_cons)
    cons_chain = LLMChain(llm=llm, prompt=cons_prompt_template, output_key="suggestion")
    
    st.toast('กำลังให้คำแนะนำ...📝')

    # get poem
    template_poem = """You are a poet. Write a 2-stanza poem in {lang} based on the 5-word summary of the suggestion. Make the poem rhyme. Be didactic.

    Suggestion:
    Girl, if he's playing games, don't waste your time waiting around. Hit him with that confidence and live your best life. You deserve someone who's as eager to text you as you are to text them!

    In love's game, don't stand still,
    With confidence, embrace the thrill,
    Don't linger in doubt's dark shade,
    Forge ahead, don't be afraid.

    Time's too precious, don't delay,
    Let go of what's causing dismay,
    With each step, a new dawn,
    In self-assurance, you'll be drawn.


    Suggestion:
    {suggestion}

    """

    prompt_template = PromptTemplate(input_variables=["lang", "suggestion"], template=template_poem)
    poem_chain = LLMChain(llm=llm, prompt=prompt_template, output_key="poem")

    st.toast('กำลังเขียนบทกลอน...📝')

    overall_chain = SequentialChain(chains=[lang_chain, cons_chain, poem_chain],
                                    input_variables=["issue", "style"],
                                    output_variables=["lang", "suggestion", "poem"],
                                    verbose=False)
    return overall_chain


# add a text input box for the user to enter their OpenAI API key.
openai_api_key = st.sidebar.text_input('OpenAI API Key', type='password')

# set page title and favicon.
st.title('🔮 :red[เซียมซี]:violet[แม่หมอ GPT]')
st.subheader("*บริการปรึกษาปัญหาใจ คลายทุกข์ผ่าน :red[บทกลอน]*")

# Add a form to the page.
with st.form('my_form'):
    # Add a text area for the user to enter their prompt.
    issue = st.text_area('ไม่สบายใจอะไร ไหนเล่าให้แม่หมอฟังซิ:', 'อยากจะขอคำแนะนำเรื่อง...')

    style_option = st.radio('อยากให้แม่หมอพูดตรง ๆ หรือเปล่าคะ?',
                     ["เบา ๆ แม่ ใจคนเรามันบาง", "ขอแรง ๆ จัดมาได้เลยแม่"])
    
    if style_option == "เบา ๆ แม่ ใจคนเรามันบาง":
        style = "gentle"
    else:
        style = "sassy"

    input_dict = {"issue":issue, "style": style}

    st.error("หลับตา ตั้งจิตอธิษฐานแล้วกดปุ่มเขย่าเซียมซี")
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
            lang = result['lang']
            st.info("แม่หมอก็พูดได้นะ... {}".format(lang))
            st.caption("แม่หมอแนะนำว่า ... ")
            poem = result['poem'].split("\n\n")
            for p in poem:
                st.write(p.replace("\n", "\n\n"))
                st.text("")
 
            with st.expander("อยากให้แม่หมออธิบายให้ฟังง่ายๆ กดที่นี่เลย 👇🏻"):
                suggestion = result['suggestion']
                st.write(suggestion)
        
        except Exception as e:
            st.error("Something went wrong!:\n{}".format(e))