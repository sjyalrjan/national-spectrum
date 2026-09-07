
import streamlit as st
import numpy as np
import librosa
import json
import os
import base64
import streamlit.components.v1 as components
from datetime import datetime

# ---------------------------------------------------------
# Page Configuration & Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="National Spectrum Mosaic | المتحف الصوتي الوطني",
    page_icon="✦",
    layout="wide"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,400;0,500;1,400&display=swap');

    .stApp {
        background: radial-gradient(circle at 50% 0%, #0D2C22 0%, #061913 38%, #020907 100%);
        color: #F5F3EE;
        font-family: 'DM Sans', sans-serif;
    }
    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }
    .hero {
        text-align: center;
        padding: 20px 0 25px 0;
    }
    .hero-kicker {
        color: #5BA88E;
        font-size: 11px;
        letter-spacing: 5px;
        text-transform: uppercase;
        margin-bottom: 12px;
    }
    .hero-title {
        font-family: 'Playfair Display', serif;
        font-size: 56px;
        line-height: 1;
        font-weight: 400;
        letter-spacing: -2px;
        margin: 0;
        color: #F4F0E8;
    }
    .hero-title span {
        color: #2CA880;
    }
    .hero-subtitle {
        color: #92B5A8;
        font-size: 14px;
        font-weight: 300;
        letter-spacing: 0.5px;
        margin-top: 15px;
    }
    .section-title {
        font-family: 'Playfair Display', serif;
        font-size: 26px;
        color: #F1EEE7;
        margin-top: 35px;
        margin-bottom: 15px;
        text-align: center;
    }
    .small-label {
        color: #5BA88E;
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 3px;
    }
    .info-box {
        background: rgba(11, 61, 46, 0.15);
        border: 1px solid rgba(44, 168, 128, 0.20);
        border-radius: 16px;
        padding: 25px;
        margin: 20px auto;
        max-width: 850px;
        text-align: center;
    }
    .dna-card {
        background: rgba(11, 61, 46, 0.22);
        border: 1px solid rgba(44, 168, 128, 0.25);
        border-radius: 14px;
        padding: 16px;
        text-align: center;
    }
    .dna-value {
        font-size: 20px;
        font-weight: 500;
        color: #62CBB0;
        margin-top: 4px;
    }
    .dna-tag {
        font-size: 11px;
        color: #92B5A8;
        margin-top: 2px;
    }
    .footer {
        text-align: center;
        color: #436B5E;
        font-size: 10px;
        letter-spacing: 3px;
        padding-top: 40px;
        line-height: 1.8;
    }
</style>
""", unsafe_allow_html=True)

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
st.markdown("""
<div class="hero">
<div class="hero-kicker">NATIONAL DAY 96 · GENERATIVE CULTURAL ARCHIVE</div>
<div class="hero-title">A Museum<br>Built by <span>Voices.</span></div>
<div class="hero-subtitle">Your voice becomes a piece of the National Spectrum.</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="info-box">
<div class="small-label">THE IDEA</div>
<h3 style="font-family:'Playfair Display'; font-weight:400; margin-top:8px; color:#F4F0E8; font-size:22px;">
What if our voices could build a sanctuary?
</h3>
<p style="color:#92B5A8; line-height:1.7; font-size:14px; margin-top:12px;">
Voices carry warmth and the breath of our land. From the northern sands to the southern peaks, every voice weaves a glowing thread into a living national tapestry—a digital museum where Saudi soundscapes pulse as one.
</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Region Options & Voice Input
# ---------------------------------------------------------
regions = {
    "Northern Region": {"heritage": "Sadu Weaving", "description": "Geometric rhythms inspired by Sadu textiles and desert landscapes.", "color": "#FF2A6D"},
    "Central Region": {"heritage": "Najdi Architecture", "description": "Terracotta geometry inspired by Najdi clay architecture.", "color": "#FFC53D"},
    "Southern Region": {"heritage": "Al-Qatt Al-Asiri", "description": "Layered geometry inspired by the colorful visual language of Al-Qatt.", "color": "#00F5D4"},
    "Western Region": {"heritage": "Rawashin & Hejaz", "description": "Vertical structures inspired by Rawashin, old Jeddah and the Red Sea.", "color": "#0066FF"},
    "Eastern Region": {"heritage": "Palm Oases", "description": "Flowing structures inspired by palms, water and the Eastern oasis.", "color": "#00E676"}
}

selected_region = st.selectbox("Choose your region", list(regions.keys()))
region_data = regions[selected_region]

st.markdown(
    f"""
    <div style="background: rgba(11, 61, 46, 0.2); border: 1px solid {region_data["color"]}66; border-radius: 16px; padding: 18px; max-width: 850px; margin: 0 auto 20px auto;">
    <div class="small-label" style="color:{region_data["color"]};">{selected_region}</div>
    <h3 style="font-family:'Playfair Display';font-weight:400;color:{region_data["color"]};margin:4px 0;">{region_data["heritage"]}</h3>
    <p style="color:#81A89B;font-size:13px;margin:0;">{region_data["description"]}</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="section-title">Give the museum your voice.</div>', unsafe_allow_html=True)

audio_file = st.file_uploader("Voice input", type=["wav", "mp3", "m4a"], label_visibility="collapsed")

if audio_file is not None:
    audio_bytes = audio_file.getvalue()
    st.audio(audio_file)
    try:
        y, sr = librosa.load(audio_file, sr=None, mono=True)
        rms = librosa.feature.rms(y=y)[0]
        rms_min, rms_max = np.min(rms), np.max(rms)
        rms_normalized = ((rms - rms_min) / (rms_max - rms_min + 1e-6))

        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        tempo_res = librosa.beat.beat_track(y=y, sr=sr)[0]
        tempo_val = float(tempo_res.item(0)) if isinstance(tempo_res, np.ndarray) and tempo_res.size > 0 else float(tempo_res)

        avg_energy = float(np.mean(rms_normalized))
        avg_frequency = float(np.mean(spectral_centroid))

        pitch_desc = "Deep Pitch" if avg_frequency < 500 else ("Balanced Pitch" if avg_frequency < 1200 else "High Pitch")
        energy_desc = "Calm Tone" if avg_energy < 0.35 else ("Vibrant Voice" if avg_energy < 0.65 else "High Intensity")
        rhythm_desc = "Steady Flow" if tempo_val < 110 else ("Dynamic Pace" if tempo_val < 150 else "Fast Cadence")

        b64_audio = base64.b64encode(audio_bytes).decode('utf-8')

        st.markdown('<div class="section-title">Your Voice Acoustic Profile</div>', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f'<div class="dna-card"><div class="small-label">Frequency</div><div class="dna-value">{int(avg_frequency)} Hz</div><div class="dna-tag">{pitch_desc}</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="dna-card"><div class="small-label">Energy</div><div class="dna-value">{avg_energy:.2f}</div><div class="dna-tag">{energy_desc}</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="dna-card"><div class="small-label">Rhythm</div><div class="dna-value">{tempo_val:.0f} BPM</div><div class="dna-tag">{rhythm_desc}</div></div>', unsafe_allow_html=True)
        c4.markdown(f'<div class="dna-card"><div class="small-label">Duration</div><div class="dna-value">{len(y)/sr:.1f}s</div><div class="dna-tag">Recorded</div></div>', unsafe_allow_html=True)

        if st.button("✨ Add Your Voice Tile to the National Spectrum"):
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
            st.success("Your voice is now woven into the national mosaic!")
            st.rerun()

    except Exception as e:
        st.error("Error processing audio")

# ---------------------------------------------------------
# Original Clean Mosaic HTML Grid + Native Click & Audio
# ---------------------------------------------------------
st.markdown('<div class="section-title">The National Spectrum Mosaic</div>', unsafe_allow_html=True)

archive = st.session_state.museum_tiles
active_tiles_count = len(archive)

MIN_SLOTS = 49
total_slots = max(MIN_SLOTS, int(np.ceil(active_tiles_count / 7.0) * 7)) + 7

tiles_html_list = []
for i in range(total_slots):
    if i < active_tiles_count:
        t = archive[i]
        energy = t.get("energy", 0.5)
        bpm = t.get("bpm", 110)
        scale = 1.08 + min(energy * 0.25, 0.3)
        speed = max(0.9, 2.5 - (bpm / 120))
        glow_radius = int(8 + energy * 25)

        audio_src = f"data:audio/wav;base64,{t.get('audio_b64', '')}" if 'audio_b64' in t else ""

        tiles_html_list.append(f"""
        <div class="tile active"
             style="--tile-color: {t['color']}; --wave-scale: {scale:.2f}; --wave-speed: {speed:.2f}s; --glow-radius: {glow_radius}px;"
             onclick="playTileAudio('{t['id']}', '{audio_src}', this)"
             title="{t['id']} • {t['region']}&#10;Frequency: {t['freq']} Hz">
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

    // Reset previous playing tiles
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
st.markdown("""
<div style="text-align:center;padding:30px 20px 10px 20px;">
<div style="font-family:'Playfair Display';font-size:30px;color:#F0ECE5;">One voice is an expression.</div>
<div style="font-family:'Playfair Display';font-size:30px;color:#2CA880;margin-top:4px;">Thousands become a nation.</div>
<div style="color:#5BA88E;font-size:11px;margin-top:14px;letter-spacing:1px;">YOUR TILE · INTEGRATED INTO THE NATIONAL MOSAIC</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="footer">NATIONAL SPECTRUMS · DESIGNED & DEVELOPED BY SAJA ALARJAN<br><span style="color:#2CA880; font-size:9px;">JOUF UNIVERSITY</span></div>', unsafe_allow_html=True)
