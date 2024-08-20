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
st.sidebar.markdown('This is an image-to-image generation chatbot using Hugging Face models by <a href="https://ai.jdavis.xyz" target="_blank">0xjdavis</a>.', unsafe_allow_html=True)

# Model selection
model_options = {
    "Stable Diffusion v1.4": "CompVis/stable-diffusion-v1-4"
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

# Check and display model status
with model_status:
    with st.spinner("Checking model status..."):
        is_model_ready = check_model_status(model_options[selected_model])
        if is_model_ready:
            st.success("Model is ready!")
        else:
            st.warning("Model is still loading. You may experience delays.")

# Main content
st.title("Hugging Face Image-to-Image Generation")
st.write(f"Image transformation powered by {selected_model} Model")

# Image upload
uploaded_file = st.file_uploader("Upload an image for reference", type=["png", "jpg", "jpeg"])
if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
    st.session_state['uploaded_image'] = Image.open(uploaded_file).convert('RGB')

# Chat interface
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Upload an image and provide a description for transformation!"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    if not huggingface_api_key:
        st.info("Please add your Hugging Face API key to continue.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    if 'uploaded_image' not in st.session_state:
        st.warning("Please upload an image before generating.")
        st.stop()

    # Prepare image
    img_byte_arr = BytesIO()
    st.session_state['uploaded_image'].save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()

    # GENERATE IMAGE
    API_URL = f"https://api-inference.huggingface.co/models/{model_options[selected_model]}"
    headers = {"Authorization": f"Bearer {huggingface_api_key}"}

    def query(payload):
        response = requests.post(API_URL, headers=headers, json=payload)
        return response

    # Prepare payload
    payload = {
        "inputs": prompt,
        "image": base64.b64encode(img_byte_arr).decode('utf-8')
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

                with st.expander("Download Image"):
                    btn = st.download_button(
                        label="Download Image",
                        data=image_bytes,
                        file_name="generated_image.png",
                        mime="image/png",
                    )
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

# Calendly and Copyright (unchanged)
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

st.sidebar.caption("©️ Copyright 2024 J. Davis")
