import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import base64

# Setting page layout
st.set_page_config(
    page_title="Hugging Face Image Generation",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Secrets
huggingface_api_key = st.secrets["huggingface_key"]

# Sidebar
st.sidebar.header("About App")
st.sidebar.markdown('This is an image generation and modification app using Hugging Face models by <a href="https://ai.jdavis.xyz" target="_blank">0xjdavis</a>.', unsafe_allow_html=True)

# Model selection
model_options = {
    # "Midjourney v6": "Kvikontent/midjourney-v6",
    # "FLUX.1-schnell": "black-forest-labs/FLUX.1-schnell",
    "Stable Diffusion v1.5": "runwayml/stable-diffusion-v1-5"  # Added for image-to-image
}
selected_model = st.sidebar.selectbox("Select Model", list(model_options.keys()))

# Calendly
st.sidebar.markdown("""
    <hr />
    <center>
    <div style="border-radius:8px;padding:8px;background:#fff";width:100%;">
    <img src="https://avatars.githubusercontent.com/u/98430977" alt="Oxjdavis" height="100" width="100" border="0" style="border-radius:50%"/>
    <br />
    <span style="height:12px;width:12px;background-color:#77e0b5;border-radius:50%;display:inline-block;"></span> <b>I'm available for new projects!</b><br />
    <a href="https://calendly.com/0xjdavis" target="_blank"><button style="background:#126ff3;color:#fff;border: 1px #126ff3 solid;border-radius:8px;padding:8px 16px;margin:10px 0">Schedule a call</button></a><br />
    </div>
    </center>
    <br />
""", unsafe_allow_html=True)

# Copyright
st.sidebar.caption("©️ Copyright 2024 J. Davis")

st.title("Hugging Face Image Generation and Modification")
st.write(f"Powered by {selected_model} Model")

# Image upload
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

# CTA BUTTON
if "messages" in st.session_state:
    url = "/Hugging%20Face%20Image%20Generation"
    st.markdown(
        f'<div><a href="{url}" target="_self" style="justify-content:center; padding: 10px 10px; background-color: #2D2D2D; color: #efefef; text-align: center; text-decoration: none; font-size: 16px; border-radius: 8px;">Clear History</a></div><br /><br />',
        unsafe_allow_html=True
    )

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "I am feeling creative today! What would you like to generate or modify an image of?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    if not huggingface_api_key:
        st.info("Please add your Hugging Face API key to continue.")
        st.stop()
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    # GENERATE OR MODIFY IMAGE
    API_URL = f"https://api-inference.huggingface.co/models/{model_options[selected_model]}"
    headers = {"Authorization": f"Bearer {huggingface_api_key}"}
    
    def query(payload):
        response = requests.post(API_URL, headers=headers, json=payload)
        return response
    
    if uploaded_file is not None:
        # Image-to-Image
        image = Image.open(uploaded_file)
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        image_str = base64.b64encode(buffered.getvalue()).decode()
        payload = {
            "inputs": prompt,
            "image": image_str
        }
    else:
        # Text-to-Image
        payload = {
            "inputs": prompt,
        }
    
    with st.spinner("Generating image..."):
        response = query(payload)
    
    if response.status_code == 200:
        image = Image.open(BytesIO(response.content))
        st.image(image, caption="Generated/Modified Image")
        
        with st.expander("View Image Details"):
            # DOWNLOAD BUTTON
            btn = st.download_button(
                label="Download Image",
                data=response.content,
                file_name="generated_image.png",
                mime="image/png",
            )
            
            # Display base64 encoded image for debugging
            st.text("Base64 Encoded Image:")
            st.text(base64.b64encode(response.content).decode())
    else:
        error_message = f"Error generating image: {response.status_code} - {response.text}"
        st.error(error_message)
        if "CUDA out of memory" in response.text:
            st.warning("The model is currently overloaded. Please try again later or try a different model.")
        elif response.status_code == 503:
            st.warning("The model is currently loading. Please try again in a few moments.")
        else:
            st.warning("An unexpected error occurred. Please check your input and try again.")

    st.session_state.messages.append({"role": "assistant", "content": "Here's the generated/modified image based on your prompt."})
