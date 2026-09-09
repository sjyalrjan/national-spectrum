
import streamlit as st
import numpy as np
import librosa
import json
import os
import base64
import streamlit.components.v1 as components
from datetime import datetime
from streamlit_mic_recorder import mic_recorder

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="National Spectrum Mosaic | فسيفساء الطيف الوطني",
    page_icon="✨",
    layout="wide"
)

# ---------------------------------------------------------
# Language State Management
# ---------------------------------------------------------
if 'lang' not in st.session_state:
    st.session_state.lang = 'ar'

# ---------------------------------------------------------
# Custom Styling & Typography
# ---------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;900&family=Playfair+Display:ital,wght@0,400;0,600;1,400&display=swap');

    html, body, [class*="css"] {
        font-family: 'Tajawal', sans-serif;
        background-color: #080A0C;
        color: #E2E8F0;
    }

    .stApp {
        background: radial-gradient(circle at 50% 0%, #111822 0%, #080A0C 75%);
    }

    /* Header styling */
    .hero-title {
        font-family: 'Tajawal', sans-serif;
        font-weight: 900;
        font-size: 2.8rem;
        background: linear-gradient(135deg, #FFFFFF 0%, #CBD5E1 50%, #2CA880 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-top: 10px;
        margin-bottom: 5px;
        letter-spacing: -0.5px;
    }

    .hero-subtitle {
        font-family: 'Tajawal', sans-serif;
        font-size: 1.1rem;
        color: #94A3B8;
        text-align: center;
        margin-bottom: 30px;
        font-weight: 400;
    }

    /* Card Box Container */
    .custom-card {
        background: rgba(15, 23, 42, 0.65);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        backdrop-filter: blur(12px);
        margin-bottom: 24px;
        box-shadow: 0 10px 30px -10px rgba(0,0,0,0.5);
    }

    .card-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #F8FAFC;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Button overrides */
    .stButton > button {
        border-radius: 10px;
        font-family: 'Tajawal', sans-serif;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    .footer {
        text-align: center;
        padding: 30px 0 10px 0;
        color: #64748B;
        font-size: 0.85rem;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
        margin-top: 50px;
    }
</style>
""", unsafe_allow_html=True)

# Language Toggle Button Top Right
col_top1, col_top2 = st.columns([8, 2])
with col_top2:
    if st.session_state.lang == 'ar':
        if st.button("🌐 Switch to English"):
            st.session_state.lang = 'en'
            st.rerun()
    else:
        if st.button("🌐 التغيير للغة العربية"):
            st.session_state.lang = 'ar'
            st.rerun()

# ---------------------------------------------------------
# Texts Translation Dictionary
# ---------------------------------------------------------
T = {
    'ar': {
        'title': 'مَتْحَفُ الطَّيْفِ الوَطَنِيِّ',
        'subtitle': 'تَجْسِيدٌ بَصَرِيٌّ حِسِّيٌّ لِلأَصْوَاتِ وَالنَّبَضَاتِ الوَطَنِيَّةِ',
        'gift_title': 'أَهْدِ صَوْتَكَ لِلْمَتْحَفِ',
        'gift_method': 'طريقة إضافة الصوت:',
        'option_rec': '🎙️ تسجيل مباشر',
        'option_file': '📁 رفع ملف صوتي',
        'rec_prompt': 'اضغط لبدء التسجيل الصوتي:',
        'upload_prompt': 'اختر ملفاً صوتياً (MP3, WAV):',
        'region_label': 'المنطقة أو الجهة:',
        'regions': ["الرياض", "مكة المكرمة", "المنطقة الشرقية", "المدينة المنورة", "عسير", "القصيم", "حائل", "تبوك", "الجوف", "جازان", "نجران", "الباحة", "الحدود الشمالية"],
        'tag_label': 'شعور أو وصف البصمة الصوتية (اختياري):',
        'tag_ph': 'مثال: اعتزاز، فرحة، نشيد، دعاء...',
        'submit_btn': 'تجسيد الصوت وحفظه في الفسيفساء ✨',
        'mosaic_title': 'فسيفساء الطيف الوطني',
        'mosaic_sub': 'كل بلاطة توثق بصمة صوتية فريدة؛ اضغط على أي بلاطة للاستماع.',
        'analytics_title': 'تحليل الخصائص الصوتية',
        'metric_pitch': 'متوسط حدة الصوت (Pitch)',
        'metric_energy': 'الطاقة والجهارة (RMS)',
        'metric_tempo': 'الإيقاع المقدر (BPM)',
        'success_msg': 'تم إضافة بصمتك الصوتية بنجاح إلى الفسيفساء الوطنية!',
        'footer': 'متحف الطيف الوطني - تم التطوير بواسطة سجى العرجان | جامعة الجوف'
    },
    'en': {
        'title': 'NATIONAL SPECTRUM MUSEUM',
        'subtitle': 'Sensory & Visual Representation of National Voices',
        'gift_title': 'Gift Your Voice to the Museum',
        'gift_method': 'Input Method:',
        'option_rec': '🎙️ Live Recording',
        'option_file': '📁 Upload Audio File',
        'rec_prompt': 'Click to record:',
        'upload_prompt': 'Choose an audio file (MP3, WAV):',
        'region_label': 'Region / Location:',
        'regions': ["Riyadh", "Makkah", "Eastern Province", "Madinah", "Asir", "Qassim", "Hail", "Tabuk", "Al-Jouf", "Jazan", "Najran", "Al-Baha", "Northern Borders"],
        'tag_label': 'Emotion or Tag (Optional):',
        'tag_ph': 'e.g., Pride, Joy, Chant, Reflection...',
        'submit_btn': 'Embody Voice & Add to Mosaic ✨',
        'mosaic_title': 'National Spectrum Mosaic',
        'mosaic_sub': 'Each tile represents a unique voice print; click any tile to listen.',
        'analytics_title': 'Audio Features Analytics',
        'metric_pitch': 'Average Pitch (Hz)',
        'metric_energy': 'RMS Energy',
        'metric_tempo': 'Estimated Tempo (BPM)',
        'success_msg': 'Your voice print has been successfully integrated into the national mosaic!',
        'footer': 'NATIONAL SPECTRUM - DESIGNED & DEVELOPED BY SAJA ALARJAN | JOUF UNIVERSITY'
    }
}

txt = T[st.session_state.lang]

# ---------------------------------------------------------
# Header Render
# ---------------------------------------------------------
st.markdown(f'<div class="hero-title">{txt["title"]}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="hero-subtitle">{txt["subtitle"]}</div>', unsafe_allow_html=True)

# Data Persistence
DATA_FILE = "spectrum_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return [
        {"id": 1, "color": "#F59E0B", "region": "Riyadh", "tag": "Pride", "audio": ""},
        {"id": 2, "color": "#10B981", "region": "Makkah", "tag": "Peace", "audio": ""},
        {"id": 3, "color": "#EC4899", "region": "Al-Jouf", "tag": "Heritage", "audio": ""},
        {"id": 4, "color": "#8B5CF6", "region": "Eastern Province", "tag": "Joy", "audio": ""}
    ]

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

tiles_data = load_data()

# ---------------------------------------------------------
# Main Layout
# ---------------------------------------------------------
col_input, col_display = st.columns([1, 1], gap="large")

with col_input:
    st.markdown(f'<div class="card-title">🎙️ {txt["gift_title"]}</div>', unsafe_allow_html=True)
    
    input_method = st.radio(
        txt['gift_method'],
        [txt['option_rec'], txt['option_file']],
        horizontal=True
    )

    audio_bytes = None

    if input_method == txt['option_rec']:
        st.write(txt['rec_prompt'])
        audio_dict = mic_recorder(
            start_prompt="🔴 " + ("بدء التسجيل" if st.session_state.lang == 'ar' else "Start Recording"),
            stop_prompt="⏹️ " + ("إيقاف التسجيل" if st.session_state.lang == 'ar' else "Stop Recording"),
            key='recorder'
        )
        if audio_dict:
            audio_bytes = audio_dict['bytes']
            st.audio(audio_bytes, format='audio/wav')
    else:
        uploaded_file = st.file_uploader(txt['upload_prompt'], type=['wav', 'mp3', 'm4a', 'ogg'])
        if uploaded_file is not None:
            audio_bytes = uploaded_file.read()
            st.audio(audio_bytes)

    region = st.selectbox(txt['region_label'], txt['regions'])
    tag = st.text_input(txt['tag_label'], placeholder=txt['tag_ph'])

    if st.button(txt['submit_btn'], use_container_width=True, type="primary"):
        if audio_bytes:
            # Color Generation from Audio Features
            try:
                import io
                y, sr = librosa.load(io.BytesIO(audio_bytes), duration=5)
                pitch = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))
                energy = float(np.mean(librosa.feature.rms(y=y)))
                
                # Map audio properties to RGB color
                r_val = int(np.clip((pitch / 4000) * 255, 50, 255))
                g_val = int(np.clip((energy * 10) * 255, 100, 240))
                b_val = int(np.clip(255 - (r_val / 2), 100, 255))
                hex_color = f"#{r_val:02x}{g_val:02x}{b_val:02x}"
            except Exception:
                hex_color = "#2CA880"

            b64_audio = base64.b64encode(audio_bytes).decode('utf-8')
            audio_uri = f"data:audio/wav;base64,{b64_audio}"

            new_tile = {
                "id": len(tiles_data) + 1,
                "color": hex_color,
                "region": region,
                "tag": tag if tag else "National Voice",
                "audio": audio_uri
            }

            tiles_data.append(new_tile)
            save_data(tiles_data)
            st.success(txt['success_msg'])
            st.rerun()
        else:
            st.warning("رجاءً سجل صوتاً أو ارفع ملفاً أولاً!" if st.session_state.lang == 'ar' else "Please record or upload audio first!")

with col_display:
    st.markdown(f'<div class="card-title">🧩 {txt["mosaic_title"]}</div>', unsafe_allow_html=True)
    st.caption(txt['mosaic_sub'])

    # Interactive HTML Mosaic Grid
    mosaic_json = json.dumps(tiles_data)
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            .mosaic-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(65px, 1fr));
                gap: 12px;
                padding: 15px;
                background: rgba(10, 15, 24, 0.8);
                border-radius: 14px;
                border: 1px solid rgba(255,255,255,0.05);
                max-height: 400px;
                overflow-y: auto;
            }}
            .tile {{
                width: 100%;
                height: 65px;
                border-radius: 12px;
                cursor: pointer;
                transition: transform 0.25s ease, box-shadow 0.25s ease;
                border: 1px solid rgba(255,255,255,0.15);
            }}
            .tile:hover {{
                transform: scale(1.1);
                box-shadow: 0 0 15px rgba(255, 255, 255, 0.4);
                z-index: 10;
            }}
            .tile.playing {{
                animation: pulse 1.2s infinite alternate;
                border: 2px solid #FFFFFF;
            }}
            @keyframes pulse {{
                0% {{ transform: scale(1.0); box-shadow: 0 0 10px currentColor; }}
                100% {{ transform: scale(1.12); box-shadow: 0 0 22px currentColor; }}
            }}
        </style>
    </head>
    <body>
        <div class="mosaic-grid" id="grid"></div>
        <audio id="audioPlayer" style="display:none;"></audio>
        <div id="info" style="margin-top: 12px; font-family: sans-serif; color: #94A3B8; font-size: 13px; text-align: center;"></div>

        <script>
            const data = {mosaic_json};
            const grid = document.getElementById('grid');
            const player = document.getElementById('audioPlayer');
            const info = document.getElementById('info');

            data.forEach(item => {{
                const tile = document.createElement('div');
                tile.className = 'tile';
                tile.style.backgroundColor = item.color;
                tile.title = `${{item.region}} - ${{item.tag}}`;

                tile.onclick = () => {{
                    document.querySelectorAll('.tile').forEach(t => t.classList.remove('playing'));
                    if(item.audio) {{
                        tile.classList.add('playing');
                        player.src = item.audio;
                        player.play();
                        info.innerHTML = `✨ <b>${{item.region}}</b> | ${{item.tag}}`;
                    }} else {{
                        info.innerHTML = `✨ <b>${{item.region}}</b> | ${{item.tag}} (Sample Tile)`;
                    }}
                }};
                grid.appendChild(tile);
            }});
        </script>
    </body>
    </html>
    """
    
    components.html(html_code, height=450)

# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------
st.markdown(f'<div class="footer">{txt["footer"]}</div>', unsafe_allow_html=True)SIGNED & DEVELOPED BY SAJA ALARJAN<br><span style="color:#2CA880; font-size:9px;">JOUF UNIVERSITY</span></div>', unsafe_allow_html=True)
