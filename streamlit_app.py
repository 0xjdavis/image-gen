import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import base64
import time

# Setting page layout
st.set_page_config(
    page_title="Hugging Face Image-to-Image Generation",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Secrets
huggingface_api_key = st.secrets["huggingface_key"]

# Sidebar
st.sidebar.header("About App")
st.sidebar.markdown('This is a zero-shot image-to-image generation chatbot using Hugging Face models by <a href="https://ai.jdavis.xyz" target="_blank">0xjdavis</a>.', unsafe_allow_html=True)

# Model selection
model_options = {
    "Stable Diffusion v1.5": "runwayml/stable-diffusion-v1-5"
}
selected_model = st.sidebar.selectbox("Select Model", list(model_options.keys()))

# Model loading status
model_status = st.sidebar.empty()

# Function to check model status
def check_model_status(model_id):
    API_URL = f"https://api-inference.huggingface.co/models/{model_id}"
    headers = {"Authorization": f"Bearer {huggingface_api_key}"}
    response = requests.get(API_URL, headers=headers)
    return response.status_code == 200

# Check and display model status with loading animation
with model_status:
    with st.spinner("Checking model status..."):
        is_model_ready = check_model_status(model_options[selected_model])
        if is_model_ready:
            st.success("Model is ready!")
        else:
            st.warning("Model is still loading. You may experience delays.")
            st.markdown(
                """
                <div class="loading-spinner">
                    <div class="spinner"></div>
                </div>
                <style>
                    .loading-spinner {
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 50px;
                    }
                    .spinner {
                        border: 4px solid #f3f3f3;
                        border-top: 4px solid #3498db;
                        border-radius: 50%;
                        width: 30px;
                        height: 30px;
                        animation: spin 1s linear infinite;
                    }
                    @keyframes spin {
                        0% { transform: rotate(0deg); }
                        100% { transform: rotate(360deg); }
                    }
                </style>
                """,
                unsafe_allow_html=True
            )

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
st.write(f"Prompted artwork powered by {selected_model} Model")

# CTA BUTTON
if "messages" in st.session_state:
    url = "/Hugging%20Face%20Text%20To%20Image%20Generation"
    st.markdown(
        f'<div><a href="{url}" target="_self" style="justify-content:center; padding: 10px 10px; background-color: #2D2D2D; color: #efefef; text-align: center; text-decoration: none; font-size: 16px; border-radius: 8px;">Clear History</a></div><br /><br />',
        unsafe_allow_html=True
    )

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "I am feeling creative today! Upload an image and tell me how you'd like to modify it."}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Image upload
uploaded_file = st.file_uploader("Upload an image to modify", type=["png", "jpg", "jpeg"])
if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

if prompt := st.chat_input():
    if not huggingface_api_key:
        st.info("Please add your Hugging Face API key to continue.")
        st.stop()
    
    if uploaded_file is None:
        st.warning("Please upload an image before entering a prompt.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # GENERATE IMAGE
    API_URL = f"https://api-inference.huggingface.co/models/{model_options[selected_model]}"
    headers = {"Authorization": f"Bearer {huggingface_api_key}"}

    def query(payload):
        response = requests.post(API_URL, headers=headers, json=payload)
        return response

    # Prepare payload
    img_bytes = uploaded_file.getvalue()
    payload = {
        "inputs": {
            "image": base64.b64encode(img_bytes).decode('utf-8'),
            "prompt": prompt
        }
    }

    with st.spinner("Generating image..."):
        max_retries = 5
        retry_delay = 10
        for attempt in range(max_retries):
            response = query(payload)
            if response.status_code == 200:
                image_bytes = response.content
                image = Image.open(BytesIO(image_bytes))
                st.image(image, caption="Generated Image")

                with st.expander("View Image Details"):
                    # DOWNLOAD BUTTON
                    btn = st.download_button(
                        label="Download Image",
                        data=image_bytes,
                        file_name="generated_image.png",
                        mime="image/png",
                    )

                    # Display base64 encoded image for debugging
                    st.text("Base64 Encoded Image:")
                    st.text(base64.b64encode(image_bytes).decode())
                break
            elif response.status_code == 503:
                error_msg = response.json()
                if "estimated_time" in error_msg:
                    wait_time = min(error_msg["estimated_time"], retry_delay)
                    st.warning(f"Model is still loading. Retrying in {wait_time:.1f} seconds...")
                    time.sleep(wait_time)
                else:
                    st.error(f"Error generating image: {response.status_code} - {response.text}")
                    break
            else:
                st.error(f"Error generating image: {response.status_code} - {response.text}")
                break
        else:
            st.error("Failed to generate image after multiple attempts. Please try again later.")

    st.session_state.messages.append({"role": "assistant", "content": f"Here's the image I generated based on your prompt: '{prompt}'"})
