
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
    page_title="National Spectrum Mosaic | المتحف الصوتي الوطني",
    page_icon="✦",
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
is_rtl = st.session_state.lang == 'ar'
text_align = "right" if is_rtl else "left"
direction = "rtl" if is_rtl else "ltr"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,400;0,500;1,400&family=Tajawal:wght@300;400;500;700&display=swap');

    html, body, [class*="css"], .stApp {{
        background: radial-gradient(circle at 50% 0%, #0D2C22 0%, #061913 38%, #020907 100%);
        color: #F5F3EE;
        font-family: 'DM Sans', 'Tajawal', sans-serif !important;
        direction: {direction};
        text-align: {text_align};
    }}
    .block-container {{
        max-width: 1200px;
        padding-top: 1rem;
        padding-bottom: 4rem;
    }}
    .hero {{
        text-align: center;
        padding: 20px 0 25px 0;
    }}
    .hero-kicker {{
        color: #5BA88E;
        font-size: 11px;
        letter-spacing: 3px;
        text-transform: uppercase;
        margin-bottom: 12px;
    }}
    .hero-title {{
        font-family: 'Tajawal', 'Playfair Display', serif;
        font-size: 48px;
        line-height: 1.2;
        font-weight: 700;
        margin: 0;
        color: #F4F0E8;
    }}
    .hero-title span {{
        color: #2CA880;
    }}
    .hero-subtitle {{
        color: #92B5A8;
        font-size: 15px;
        font-weight: 300;
        margin-top: 15px;
    }}
    .section-title {{
        font-family: 'Tajawal', 'Playfair Display', serif;
        font-size: 24px;
        font-weight: 700;
        color: #F1EEE7;
        margin-top: 35px;
        margin-bottom: 15px;
        text-align: center;
    }}
    .small-label {{
        color: #5BA88E;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 2px;
    }}
    .info-box {{
        background: rgba(11, 61, 46, 0.15);
        border: 1px solid rgba(44, 168, 128, 0.20);
        border-radius: 16px;
        padding: 25px;
        margin: 20px auto;
        max-width: 850px;
        text-align: center;
    }}
    .dna-card {{
        background: rgba(11, 61, 46, 0.22);
        border: 1px solid rgba(44, 168, 128, 0.25);
        border-radius: 14px;
        padding: 16px;
        text-align: center;
    }}
    .dna-value {{
        font-size: 20px;
        font-weight: 500;
        color: #62CBB0;
        margin-top: 4px;
    }}
    .dna-tag {{
        font-size: 12px;
        color: #92B5A8;
        margin-top: 2px;
    }}
    .footer {{
        text-align: center;
        color: #436B5E;
        font-size: 11px;
        letter-spacing: 2px;
        padding-top: 40px;
        line-height: 1.8;
    }}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Dictionary for Translations
# ---------------------------------------------------------
t = {
    'ar': {
        'lang_btn': "🌐 English",
        'hero_kicker': "اليوم الوطني 96 · أرشيف ثقافي توليدي",
        'hero_title': "متحف يُبنى بـ <span>الأصوات.</span>",
        'hero_sub': "صوتك يتجسد كجزء لا يتجزأ من الطيف الوطني.",
        'idea_label': "الفكرة",
        'idea_title': "ماذا لو استطاعت أصواتنا بناء صرحٍ يجمعنا؟",
        'idea_desc': "تحمل أصواتنا دفء الوطن ونبض أرضه. من رمال الشمال إلى قمم الجنوب، ينسج كل صوت خيطاً متوهجاً في نسيج وطني حي—متحف رقمي تتناغم فيه النبرات السعودية لتصبح لوحة واحدة.",
        'choose_region': "اختر منطقتك",
        'section_input': "اهْدِ صَوْتَكَ لِلْمَتْحَفِ",
        'input_method': "طريقة إضافة الصوت:",
        'method_mic': "تسجيل مباشر 🎙️",
        'method_upload': "رفع ملف صوتي 📁",
        'mic_start': "ابدأ التسجيل 🎙️",
        'mic_stop': "إيقاف وحفظ ⏹️",
        'upload_label': "اختر ملف صوتي من جهازك",
        'dna_title': "البصمة الصوتية والبصرية لصوتك",
        'freq': "التردد",
        'energy': "الطاقة",
        'rhythm': "الإيقاع",
        'duration': "المدة",
        'recorded': "تم التسجيل",
        'add_btn': "✨ أضف بصمتك الصوتية إلى الطيف الوطني",
        'success': "تم إضافة بصمتك الصوتية بنجاح إلى الموزاييك الوطنية!",
        'mosaic_title': "موزاييك الطيف الوطني",
        'quote_1': "صوتٌ واحدٌ إفصاحٌ وتعبير.",
        'quote_2': "وآلاف الأصواتِ وطنٌ يكتمل.",
        'tile_sub': "بصمتك الرقمية · مدمجة في الموزاييك الوطنية",
        'pitch_deep': "نبرة عميقة", 'pitch_bal': "نبرة متوازنة", 'pitch_high': "نبرة حادة",
        'eng_calm': "صوت هادئ", 'eng_vib': "صوت حيوي", 'eng_high': "كثافة عالية",
        'rhy_steady': "تدفق منتظم", 'rhy_dyn': "سرعة ديناميكية", 'rhy_fast': "إيقاع سريع",
        'n_region': "المنطقة الشمالية", 'n_heritage': "نقوش السدو الأصيل", 'n_desc': "إيقاعات هندسية مستوحاة من ألوان ونقوش السدو وصحراء الشمال.",
        'c_region': "المنطقة الوسطى", 'c_heritage': "العمارة النجدية", 'c_desc': "دلالة على العمارة النجدية ورمال الصحراء الذهبية.",
        's_region': "المنطقة الجنوبية", 's_heritage': "فن القط العسيري", 'c_s_desc': "طبقات هندسية مستوحاة من ألوان التراث الجنوبي وقمم السروات.",
        'w_region': "المنطقة الغربية", 'w_heritage': "الرواشين والتراث الساحلي", 'w_desc': "تجسيد لعمق البحر الأحمر والتراث المعماري لجدة التاريخية.",
        'e_region': "المنطقة الشرقية", 'e_heritage': "واحات النخيل والخليج", 'e_desc': "تعبير عن امتداد الخليج العربي وإرث الواحات الخضراء."
    },
    'en': {
        'lang_btn': "🌐 عربي",
        'hero_kicker': "NATIONAL DAY 96 · GENERATIVE CULTURAL ARCHIVE",
        'hero_title': "A Museum Built by <span>Voices.</span>",
        'hero_sub': "Your voice becomes a piece of the National Spectrum.",
        'idea_label': "THE IDEA",
        'idea_title': "What if our voices could build a sanctuary?",
        'idea_desc': "Voices carry warmth and the breath of our land. From the northern sands to the southern peaks, every voice weaves a glowing thread into a living national tapestry—a digital museum where Saudi soundscapes pulse as one.",
        'choose_region': "Choose your region",
        'section_input': "Give the museum your voice.",
        'input_method': "Choose audio input method:",
        'method_mic': "Live Recording 🎙️",
        'method_upload': "Upload Audio File 📁",
        'mic_start': "Start Recording 🎙️",
        'mic_stop': "Stop & Save ⏹️",
        'upload_label': "Choose an audio file from your device",
        'dna_title': "Your Voice Acoustic Profile",
        'freq': "Frequency",
        'energy': "Energy",
        'rhythm': "Rhythm",
        'duration': "Duration",
        'recorded': "Recorded",
        'add_btn': "✨ Add Your Voice Tile to the National Spectrum",
        'success': "Your voice is now woven into the national mosaic!",
        'mosaic_title': "The National Spectrum Mosaic",
        'quote_1': "One voice is an expression.",
        'quote_2': "Thousands become a nation.",
        'tile_sub': "YOUR TILE · INTEGRATED INTO THE NATIONAL MOSAIC",
        'pitch_deep': "Deep Pitch", 'pitch_bal': "Balanced Pitch", 'pitch_high': "High Pitch",
        'eng_calm': "Calm Tone", 'eng_vib': "Vibrant Voice", 'eng_high': "High Intensity",
        'rhy_steady': "Steady Flow", 'rhy_dyn': "Dynamic Pace", 'rhy_fast': "Fast Cadence",
        'n_region': "Northern Region", 'n_heritage': "Sadu Weaving", 'n_desc': "Geometric rhythms inspired by Sadu textiles and desert landscapes.",
        'c_region': "Central Region", 'c_heritage': "Najdi Architecture", 'c_desc': "Terracotta geometry inspired by Najdi clay architecture.",
        's_region': "Southern Region", 's_heritage': "Al-Qatt Al-Asiri", 'c_s_desc': "Layered geometry inspired by the colorful visual language of Al-Qatt.",
        'w_region': "Western Region", 'w_heritage': "Rawashin & Hejaz", 'w_desc': "Vertical structures inspired by Rawashin, old Jeddah and the Red Sea.",
        'e_region': "Eastern Region", 'e_heritage': "Palm Oases", 'e_desc': "Flowing structures inspired by palms, water and the Eastern oasis."
    }
}[st.session_state.lang]

# ---------------------------------------------------------
# Top Navigation Bar & Language Switcher
# ---------------------------------------------------------
col_blank, col_lang_btn = st.columns([8, 2])
with col_lang_btn:
    if st.button(t['lang_btn'], key="lang_toggle"):
        st.session_state.lang = 'en' if st.session_state.lang == 'ar' else 'ar'
        st.rerun()

# ---------------------------------------------------------
# Data Persistence
# ---------------------------------------------------------
DATA_FILE = "museum_mosaic_data.json"

def load_archive():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_to_archive(entry):
    archive = load_archive()
    archive.append(entry)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(archive, f, ensure_ascii=False, indent=2)

if "museum_tiles" not in st.session_state:
    st.session_state.museum_tiles = load_archive()

# ---------------------------------------------------------
# Hero & Info Box
# ---------------------------------------------------------
st.markdown(f"""
<div class="hero">
    <div class="hero-kicker">{t['hero_kicker']}</div>
    <div class="hero-title">{t['hero_title']}</div>
    <div class="hero-subtitle">{t['hero_sub']}</div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="info-box">
    <div class="small-label">{t['idea_label']}</div>
    <h3 style="font-family:'Tajawal', 'Playfair Display'; font-weight:700; margin-top:8px; color:#F4F0E8; font-size:22px;">
    {t['idea_title']}
    </h3>
    <p style="color:#92B5A8; line-height:1.7; font-size:14px; margin-top:12px;">
    {t['idea_desc']}
    </p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Region Options & Voice Input
# ---------------------------------------------------------
regions = {
    t['n_region']: {"heritage": t['n_heritage'], "description": t['n_desc'], "color": "#FF2A6D"},
    t['c_region']: {"heritage": t['c_heritage'], "description": t['c_desc'], "color": "#FFC53D"},
    t['s_region']: {"heritage": t['s_heritage'], "description": t['c_s_desc'], "color": "#00F5D4"},
    t['w_region']: {"heritage": t['w_heritage'], "description": t['w_desc'], "color": "#0066FF"},
    t['e_region']: {"heritage": t['e_heritage'], "description": t['e_desc'], "color": "#00E676"}
}

selected_region = st.selectbox(t['choose_region'], list(regions.keys()))
region_data = regions[selected_region]

st.markdown(
    f"""
    <div style="background: rgba(11, 61, 46, 0.2); border: 1px solid {region_data["color"]}66; border-radius: 16px; padding: 18px; max-width: 850px; margin: 0 auto 20px auto; text-align:{text_align};">
    <div class="small-label" style="color:{region_data["color"]};">{selected_region}</div>
    <h3 style="font-family:'Tajawal', 'Playfair Display';font-weight:700;color:{region_data["color"]};margin:4px 0;">{region_data["heritage"]}</h3>
    <p style="color:#81A89B;font-size:13px;margin:0;">{region_data["description"]}</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(f'<div class="section-title">{t["section_input"]}</div>', unsafe_allow_html=True)

# Audio Input Switcher (Mic or Upload)
input_option = st.radio(t['input_method'], (t['method_mic'], t['method_upload']), horizontal=True)

audio_bytes = None

if input_option == t['method_mic']:
    audio_data = mic_recorder(
        start_prompt=t['mic_start'],
        stop_prompt=t['mic_stop'],
        key='recorder'
    )
    if audio_data is not None:
        audio_bytes = audio_data['bytes']
else:
    uploaded_file = st.file_uploader(t['upload_label'], type=["wav", "mp3", "m4a"], label_visibility="collapsed")
    if uploaded_file is not None:
        audio_bytes = uploaded_file.getvalue()

if audio_bytes is not None:
    st.audio(audio_bytes)
    try:
        # Load audio for librosa processing
        import io
        audio_stream = io.BytesIO(audio_bytes)
        y, sr = librosa.load(audio_stream, sr=None, mono=True)
        
        rms = librosa.feature.rms(y=y)[0]
        rms_min, rms_max = np.min(rms), np.max(rms)
        rms_normalized = ((rms - rms_min) / (rms_max - rms_min + 1e-6))

        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        tempo_res = librosa.beat.beat_track(y=y, sr=sr)[0]
        tempo_val = float(tempo_res.item(0)) if isinstance(tempo_res, np.ndarray) and tempo_res.size > 0 else float(tempo_res)

        avg_energy = float(np.mean(rms_normalized))
        avg_frequency = float(np.mean(spectral_centroid))

        pitch_desc = t['pitch_deep'] if avg_frequency < 500 else (t['pitch_bal'] if avg_frequency < 1200 else t['pitch_high'])
        energy_desc = t['eng_calm'] if avg_energy < 0.35 else (t['eng_vib'] if avg_energy < 0.65 else t['eng_high'])
        rhythm_desc = t['rhy_steady'] if tempo_val < 110 else (t['rhy_dyn'] if tempo_val < 150 else t['rhy_fast'])

        b64_audio = base64.b64encode(audio_bytes).decode('utf-8')

        st.markdown(f'<div class="section-title">{t["dna_title"]}</div>', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f'<div class="dna-card"><div class="small-label">{t["freq"]}</div><div class="dna-value">{int(avg_frequency)} Hz</div><div class="dna-tag">{pitch_desc}</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="dna-card"><div class="small-label">{t["energy"]}</div><div class="dna-value">{avg_energy:.2f}</div><div class="dna-tag">{energy_desc}</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="dna-card"><div class="small-label">{t["rhythm"]}</div><div class="dna-value">{tempo_val:.0f} BPM</div><div class="dna-tag">{rhythm_desc}</div></div>', unsafe_allow_html=True)
        c4.markdown(f'<div class="dna-card"><div class="small-label">{t["duration"]}</div><div class="dna-value">{len(y)/sr:.1f}s</div><div class="dna-tag">{t["recorded"]}</div></div>', unsafe_allow_html=True)

        if st.button(t['add_btn']):
            new_tile = {
                "id": f"SPECTRUM-{len(st.session_state.museum_tiles)+1:03d}",
                "region": selected_region,
                "color": region_data["color"],
                "energy": round(avg_energy, 3),
                "freq": int(avg_frequency),
                "bpm": int(tempo_val),
                "audio_b64": b64_audio,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            st.session_state.museum_tiles.append(new_tile)
            save_to_archive(new_tile)
            st.success(t['success'])
            st.rerun()

    except Exception as e:
        st.error(f"Error processing audio: {e}")

# ---------------------------------------------------------
# Original Clean Mosaic HTML Grid + Native Click & Audio
# ---------------------------------------------------------
st.markdown(f'<div class="section-title">{t["mosaic_title"]}</div>', unsafe_allow_html=True)

archive = st.session_state.museum_tiles
active_tiles_count = len(archive)

MIN_SLOTS = 49
total_slots = max(MIN_SLOTS, int(np.ceil(active_tiles_count / 7.0) * 7)) + 7

tiles_html_list = []
for i in range(total_slots):
    if i < active_tiles_count:
        tile_item = archive[i]
        energy = tile_item.get("energy", 0.5)
        bpm = tile_item.get("bpm", 110)
        scale = 1.08 + min(energy * 0.25, 0.3)
        speed = max(0.9, 2.5 - (bpm / 120))
        glow_radius = int(8 + energy * 25)

        audio_src = f"data:audio/wav;base64,{tile_item.get('audio_b64', '')}" if 'audio_b64' in tile_item else ""

        tiles_html_list.append(f"""
        <div class="tile active"
             style="--tile-color: {tile_item['color']}; --wave-scale: {scale:.2f}; --wave-speed: {speed:.2f}s; --glow-radius: {glow_radius}px;"
             onclick="playTileAudio('{tile_item['id']}', '{audio_src}', this)"
             title="{tile_item['id']} • {tile_item['region']}&#10;Frequency: {tile_item['freq']} Hz">
        </div>
        """)
    else:
        tiles_html_list.append('<div class="tile empty"></div>')

mosaic_grid_html = "".join(tiles_html_list)

mosaic_component = f"""
<!DOCTYPE html>
<html>
<head>
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500&display=swap');
    body {{
        margin: 0;
        background: transparent;
        font-family: 'DM Sans', sans-serif;
        color: #F5F3EE;
    }}
    .mosaic-box {{
        display: flex;
        justify-content: center;
        width: 100%;
    }}
    .mosaic-grid {{
        display: grid;
        grid-template-columns: repeat(7, 46px);
        gap: 12px;
        background: rgba(4, 20, 15, 0.65);
        border: 1px solid rgba(44, 168, 128, 0.22);
        border-radius: 20px;
        padding: 24px;
        box-shadow: inset 0 0 30px rgba(0,0,0,0.5);
    }}
    .tile {{
        width: 46px;
        height: 46px;
        border-radius: 10px;
        transition: transform 0.25s ease, box-shadow 0.25s ease;
    }}
    .tile.empty {{
        background: rgba(44, 168, 128, 0.04);
        border: 1px dashed rgba(44, 168, 128, 0.12);
    }}
    .tile.active {{
        background-color: var(--tile-color);
        box-shadow: 0 0 10px var(--tile-color);
        animation: wavePulse var(--wave-speed) infinite ease-in-out;
        cursor: pointer;
    }}
    .tile.active:hover {{
        transform: scale(1.15) !important;
        box-shadow: 0 0 20px var(--tile-color) !important;
        z-index: 10;
    }}
    .tile.playing {{
        animation: none !important;
        border: 2px solid #FFFFFF !important;
        box-shadow: 0 0 25px #FFFFFF !important;
        transform: scale(1.1) !important;
    }}
    @keyframes wavePulse {{
        0% {{ transform: scale(1); box-shadow: 0 0 6px var(--tile-color); }}
        50% {{ transform: scale(var(--wave-scale)); box-shadow: 0 0 var(--glow-radius) var(--tile-color); }}
        100% {{ transform: scale(1); box-shadow: 0 0 6px var(--tile-color); }}
    }}
    #status-bar {{
        text-align: center;
        margin-top: 15px;
        font-size: 13px;
        color: #92B5A8;
        min-height: 20px;
    }}
</style>
</head>
<body>
<div class="mosaic-box">
    <div class="mosaic-grid">
        {mosaic_grid_html}
    </div>
</div>
<div id="status-bar"></div>
<audio id="museum-player" style="display:none;"></audio>

<script>
function playTileAudio(tileId, audioSrc, element) {{
    var player = document.getElementById('museum-player');
    var status = document.getElementById('status-bar');

    var activeTiles = document.querySelectorAll('.tile.active');
    activeTiles.forEach(function(t) {{ t.classList.remove('playing'); }});

    if (audioSrc) {{
        element.classList.add('playing');
        player.src = audioSrc;
        player.play();
        status.innerHTML = "<b>Now Playing:</b> " + tileId;
    }}
}}
</script>
</body>
</html>
"""

components.html(mosaic_component, height=total_slots * 10 + 200)

# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------
st.markdown(f"""
<div style="text-align:center;padding:30px 20px 10px 20px;">
<div style="font-family:'Tajawal', 'Playfair Display';font-size:28px;font-weight:700;color:#F0ECE5;">{t['quote_1']}</div>
<div style="font-family:'Tajawal', 'Playfair Display';font-size:28px;font-weight:700;color:#2CA880;margin-top:4px;">{t['quote_2']}</div>
<div style="color:#5BA88E;font-size:11px;margin-top:14px;letter-spacing:1px;">{t['tile_sub']}</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="footer">NATIONAL SPECTRUMS · DESIGNED & DEVELOPED BY SAJA ALARJAN<br><span style="color:#2CA880; font-size:9px;">JOUF UNIVERSITY</span></div>', unsafe_allow_html=True)
