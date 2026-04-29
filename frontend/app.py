import streamlit as st
import requests
import os

# 4. Define backend URL
BACKEND_URL = 'http://localhost:8000'

st.set_page_config(page_title='AnimateDiff Video Generator', layout='wide')

# 5. UI Header and Prompt Input
st.title('🎬 AnimateDiff Text-to-Video')

prompt_input = st.text_input('Enter your prompt:', placeholder='e.g., a cat running in a field')

# 6. Style Selection
style = st.selectbox('Choose a Style:', ['Cinematic', 'Anime', 'Realistic'])
style_prompts = {
    'Cinematic': ', highly detailed, 8k, cinematic lighting, masterpiece',
    'Anime': ', anime style, high quality, vibrant colors',
    'Realistic': ', photorealistic, ultra-realistic, 4k, raw photo'
}

# 7. Generate Button and Request
if st.button('Generate Video'):
    if prompt_input:
        full_prompt = f"{prompt_input}{style_prompts[style]}"
        with st.spinner('Generating your video... this may take a minute.'):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/generate-video",
                    json={'prompt': full_prompt}
                )
                
                if response.status_code == 200:
                    # 8. Display Generated Video
                    video_data = response.json()
                    video_path = video_data.get('video_path')
                    if os.path.exists(video_path):
                        st.success('Video Generated Successfully!')
                        st.video(video_path)
                    else:
                        st.error(f'Video file not found at {video_path}')
                else:
                    st.error(f'Error from backend: {response.text}')
            except Exception as e:
                st.error(f'Connection failed: {e}')
    else:
        st.warning('Please enter a prompt first.')

# 9. History Section
st.divider()
st.subheader('📜 Generation History')

try:
    history_response = requests.get(f"{BACKEND_URL}/history")
    if history_response.status_code == 200:
        history_data = history_response.json()
        if history_data:
            for item in history_data:
                with st.expander(f"{item['created_at']} - {item['prompt'][:50]}..."):
                    st.write(f"**Full Prompt:** {item['prompt']}")
                    if os.path.exists(item['video_path']):
                        st.video(item['video_path'])
                    else:
                        st.info('Video file unavailable')
        else:
            st.write('No history found yet.')
except Exception as e:
    st.write('Could not load history.')