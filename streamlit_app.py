import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import base64

# Setting page layout
st.set_page_config(
    page_title="Hugging Face Image-to-Image Generation",
    page_icon="🖼️",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Secrets
huggingface_api_key = st.secrets["huggingface_key"]

# Sidebar
st.sidebar.header("About App")
st.sidebar.markdown('This is an image-to-image generation app using Hugging Face models by <a href="https://ai.jdavis.xyz" target="_blank">0xjdavis</a>.', unsafe_allow_html=True)

# Model selection
model_options = {
    "stable-diffusion-xl-refiner-1.0": "stabilityai/stable-diffusion-xl-refiner-1.0",
    "stable-diffusion-2-1": "stabilityai/stable-diffusion-2-1",
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

st.title("Hugging Face Image-to-Image Generation")
st.write(f"Image transformation powered by {selected_model} Model")

# Image upload
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Display the uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)
    
    # Prompt for image transformation
    prompt = st.text_input("Enter a prompt to transform the image:")
    
    if st.button("Generate New Image"):
        if not huggingface_api_key:
            st.error("Please add your Hugging Face API key to continue.")
            st.stop()
        
        # Prepare the image for API
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        image_str = base64.b64encode(buffered.getvalue()).decode()
        
        # API call
        API_URL = f"https://api-inference.huggingface.co/models/{model_options[selected_model]}"
        headers = {"Authorization": f"Bearer {huggingface_api_key}"}
        
        payload = {
            "inputs": {
                "image": image_str,
                "prompt": prompt
            }
        }
        
        with st.spinner("Generating new image..."):
            response = requests.post(API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            # Successfully received the image
            image_bytes = response.content
            generated_image = Image.open(BytesIO(image_bytes))
            st.image(generated_image, caption="Generated Image", use_column_width=True)
            
            # Download button
            buffered_output = BytesIO()
            generated_image.save(buffered_output, format="PNG")
            img_str = base64.b64encode(buffered_output.getvalue()).decode()
            href = f'<a href="data:file/png;base64,{img_str}" download="generated_image.png">Download Generated Image</a>'
            st.markdown(href, unsafe_allow_html=True)
        else:
            st.error(f"Error generating image: {response.status_code} - {response.text}")

# CTA BUTTON
url = "/Hugging%20Face%20Image%20To%20Image%20Generation"
st.markdown(
    f'<div><a href="{url}" target="_self" style="justify-content:center; padding: 10px 10px; background-color: #2D2D2D; color: #efefef; text-align: center; text-decoration: none; font-size: 16px; border-radius: 8px;">Clear History</a></div><br /><br />',
    unsafe_allow_html=True
)
