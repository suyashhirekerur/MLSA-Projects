import streamlit as st
try:
    import pyfiglet
    pyfiglet_available = True
except ImportError:
    pyfiglet = None
    pyfiglet_available = False
from PIL import Image, ImageDraw, ImageFont
import io
import os
from datetime import datetime
import json
import base64
import re
from urllib.parse import urlencode
import time
import math

# Set page config
st.set_page_config(
    page_title="ASCII Art Generator",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for terminal-style UI
terminal_css = """
<style>
    :root {
        --bg-dark: #0a0e27;
        --bg-light: #f5f5f5;
        --text-dark: #00ff00;
        --text-light: #000;
        --border-color: #00ff00;
        --accent: #ff00ff;
    }
    
    body {
        font-family: 'Courier New', monospace;
    }
    
    .terminal-output {
        background-color: var(--bg-dark);
        color: var(--text-dark);
        border: 2px solid var(--border-color);
        padding: 20px;
        border-radius: 5px;
        font-family: 'Courier New', monospace;
        min-height: 200px;
        overflow-x: auto;
        overflow-y: auto;
        max-height: 600px;
        line-height: 1.2;
        white-space: pre;
    }
    
    .terminal-output.light {
        background-color: var(--bg-light);
        color: var(--text-light);
        border-color: #333;
    }
    
    .ascii-preview {
        font-size: 12px;
        word-break: break-all;
        white-space: pre-wrap;
        margin: 0;
    }
    
    .info-box {
        background-color: rgba(0, 255, 0, 0.1);
        border-left: 4px solid #00ff00;
        padding: 10px;
        margin: 10px 0;
        border-radius: 3px;
    }
    
    .info-box.light {
        background-color: rgba(0, 0, 0, 0.05);
        border-left-color: #333;
    }
    
    .gallery-item {
        border: 1px solid #00ff00;
        padding: 10px;
        margin: 10px 0;
        border-radius: 3px;
        font-size: 10px;
    }
    
    .gallery-item.light {
        border-color: #333;
    }
</style>
"""

# Apply theme-specific CSS dynamically
if 'theme' in st.session_state and st.session_state.theme == 'light':
    st.markdown("""
    <style>
        :root {
            --bg-dark: #f5f5f5 !important;
            --text-dark: #000 !important;
            --border-color: #333 !important;
        }
        .terminal-output {
            background-color: var(--bg-dark) !important;
            color: var(--text-dark) !important;
            border-color: var(--border-color) !important;
        }
    </style>
    """, unsafe_allow_html=True)

st.markdown(terminal_css, unsafe_allow_html=True)

if not pyfiglet_available:
    st.warning(
        "The pyfiglet package is not installed. Text-to-ASCII features are disabled until pyfiglet is added to requirements.txt and the app is redeployed."
    )

# Initialize session state
if 'gallery' not in st.session_state:
    st.session_state.gallery = []

if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

if 'current_art' not in st.session_state:
    st.session_state.current_art = ""

def ansi_to_html(text):
    """Convert ANSI color codes to HTML spans"""
    # Simple ANSI to HTML conversion
    ansi_pattern = r'\033\[38;2;(\d+);(\d+);(\d+)m(.*?)\033\[0m'
    def replace_ansi(match):
        r, g, b, content = match.groups()
        return f'<span style="color: rgb({r},{g},{b})">{content}</span>'
    
    # Remove any remaining ANSI codes
    text = re.sub(r'\033\[[0-9;]*m', '', text)
    return text

def create_colored_html(art, color1, color2=None, gradient=False):
    """Create HTML with proper coloring"""
    if not art:
        return art
    
    if gradient and color2:
        # Apply gradient coloring
        lines = art.split('\n')
        result = []
        char_count = 0
        total_chars = sum(len(line) for line in lines)
        
        for line in lines:
            colored_line = ""
            for char in line:
                if char != ' ' and char != '\n':
                    # Calculate gradient position
                    ratio = char_count / max(total_chars, 1)
                    
                    # Interpolate between colors
                    r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
                    r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
                    
                    r = int(r1 + (r2 - r1) * ratio)
                    g = int(g1 + (g2 - g1) * ratio)
                    b = int(b1 + (b2 - b1) * ratio)
                    
                    colored_line += f'<span style="color: rgb({r},{g},{b})">{char}</span>'
                else:
                    colored_line += char
                char_count += 1
            result.append(colored_line)
        return '\n'.join(result)
    else:
        # Single color
        r, g, b = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
        return f'<span style="color: rgb({r},{g},{b})">{art}</span>'

def get_pyfiglet_fonts():
    """Get list of available pyfiglet fonts"""
    if not pyfiglet_available:
        return ['standard']

    fonts = [
        'big', 'banner', 'block', 'bubble', 'digital', 'ivrit', 'lean',
        'mini', 'script', 'shadow', 'slant', 'small', 'smscript', 'smshadow',
        'smslant', 'standard', 'term', '3-d', '3d-ascii', 'doom', 'epic',
        'graffiti', 'gothic', 'graceful', 'gradient', 'heavy', 'hex', 'jazmine',
        'nancyj', 'ogre', 'poison', 'puffy', 'rectangles', 'relief', 'roman',
        'rot13', 'rounded', 'rows', 'runic', 'script', 'serifcap', 'short',
        'skeleton', 'slant', 'slide', 'small', 'smproms', 'smshadow', 'smslant',
        'smten', 'speed', 'spiral', 'stacey', 'standard', 'starwars', 'stencil',
        'stepped', 'stick', 'stop', 'straight', 'times', 'tinker-toy', 'twisted',
        'two-point', 'univers'
    ]
    return sorted(list(set(fonts)))

def generate_ascii_art(text, font, alignment, spacing):
    """Generate ASCII art from text"""
    if not pyfiglet_available:
        return "Error: The pyfiglet package is not installed. Please add pyfiglet to requirements.txt and redeploy."

    try:
        fig = pyfiglet.Figlet(font=font, width=120)
        art = fig.renderText(text)
        
        # Apply alignment
        lines = art.split('\n')
        if alignment == 'center':
            max_width = max(len(line) for line in lines) if lines else 0
            lines = [line.center(max_width) for line in lines]
        elif alignment == 'right':
            max_width = max(len(line) for line in lines) if lines else 0
            lines = [line.rjust(max_width) for line in lines]
        
        art = '\n'.join(lines)
        
        # Apply spacing
        if spacing > 1:
            lines = art.split('\n')
            spaced_lines = []
            for line in lines:
                spaced_line = ' '.join(line)
                spaced_lines.append(spaced_line)
            art = '\n'.join(spaced_lines)
        
        return art
    except Exception as e:
        return f"Error: {str(e)}"

def add_border(text, border_style):
    """Add border to ASCII art"""
    lines = text.split('\n')
    max_width = max(len(line) for line in lines) if lines else 0
    
    borders = {
        'single': ('┌', '─', '┐', '│', '└', '┘'),
        'double': ('╔', '═', '╗', '║', '╚', '╝'),
        'rounded': ('╭', '─', '╮', '│', '╰', '╯'),
        'dashed': ('┏', '┅', '┓', '┃', '┗', '┛'),
        'starred': ('*', '*', '*', '*', '*', '*'),
        'hash': ('#', '#', '#', '#', '#', '#'),
        'equals': ('=', '=', '=', '|', '=', '='),
    }
    
    if border_style not in borders:
        return text
    
    tl, h, tr, v, bl, br = borders[border_style]
    
    result = tl + h * (max_width + 2) + tr + '\n'
    for line in lines:
        result += v + ' ' + line.ljust(max_width) + ' ' + v + '\n'
    result += bl + h * (max_width + 2) + br
    
    return result

def apply_effects(text, effect):
    """Apply visual effects to ASCII art"""
    if effect == 'invert':
        return text.replace('█', '░').replace('▓', '▒').replace('▒', '▓').replace('░', '█')
    elif effect == 'flip_horizontal':
        lines = text.split('\n')
        return '\n'.join(line[::-1] for line in lines)
    elif effect == 'flip_vertical':
        lines = text.split('\n')
        return '\n'.join(reversed(lines))
    elif effect == 'bold':
        return text.replace(' ', '  ')
    else:
        return text

def image_to_ascii(image, density='medium', width=80):
    """Convert image to ASCII art"""
    try:
        img = Image.open(image).convert('L')
        
        aspect_ratio = img.height / img.width
        new_height = int(width * aspect_ratio * 0.55)
        
        img = img.resize((width, new_height))
        
        char_sets = {
            'light': '.:-=+*#%@',
            'medium': '@%#*+=-:.',
            'dense': '@█▓▒░ ▀▄▌▐█'
        }
        
        chars = char_sets.get(density, char_sets['medium'])
        
        pixels = img.getdata()
        ascii_art = ''
        for i, pixel in enumerate(pixels):
            if i % width == 0:
                ascii_art += '\n'
            ascii_art += chars[int((pixel / 255) * (len(chars) - 1))]
        
        return ascii_art
    except Exception as e:
        return f"Error converting image: {str(e)}"

def emoji_to_ascii(emoji):
    """Convert emoji to ASCII representation"""
    emoji_map = {
        '😀': ':D', '😃': ':-D', '😄': ':D', '😁': ':D',
        '😆': ':D', '😅': ':-D', '😂': ":'D", '🤣': ":'D",
        '😊': ':)', '😇': 'O:)', '🙂': ':)', '🙃': ':(',
        '😉': ';)', '😌': ':|', '😍': '<3', '😘': ':-*',
        '😗': ':-*', '😚': ':-*', '😙': ':-*', '😗': ':-*',
        '🥰': '<3', '😋': ':p', '😛': ':p', '😜': ';p',
        '🤪': ';p', '😝': ':p', '😑': ':|', '😐': ':|',
        '😶': ':-*', '🙁': ':(', '☹️': ':(', '😏': ':|',
        '😒': ':|', '😞': ':(', '😔': ':(', '😫': ':(',
        '😩': ':(', '🥺': ':\'(', '😠': '>:(', '😡': '>:(',
        '😤': '>:(', '😠': '>:(', '🤬': '>:(', '😈': '>:(',
        '👿': '>:(', '💀': ':x', '☠️': ':x', '💩': ':p',
        '🤡': ':)', '👹': '>:(', '👺': '>:(', '👻': ':o',
        '👽': ':o', '👾': ':o', '🤖': ':|', '😺': ':)',
        '😸': ':D', '😹': ':D', '😻': '<3', '😼': ':|',
        '😽': ':p', '🙀': ':o', '😿': ':(', '😾': '>:(',
    }
    return emoji_map.get(emoji, emoji)

def save_to_gallery(name, art, settings):
    """Save ASCII art to gallery"""
    item = {
        'name': name,
        'art': art,
        'settings': settings,
        'timestamp': datetime.now().isoformat()
    }
    st.session_state.gallery.append(item)

def export_as_html(art, title="ASCII Art"):
    """Export ASCII art as HTML"""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{title}</title>
        <style>
            body {{ font-family: 'Courier New', monospace; background: #0a0e27; color: #00ff00; }}
            pre {{ padding: 20px; border: 2px solid #00ff00; }}
        </style>
    </head>
    <body>
        <h1>{title}</h1>
        <pre>{art}</pre>
    </body>
    </html>
    """
    return html

def export_as_png(art, filename="ascii_art.png"):
    """Export ASCII art as PNG image"""
    try:
        lines = art.split('\n')
        char_width, char_height = 8, 12
        
        width = max(len(line) for line in lines) * char_width + 40
        height = len(lines) * char_height + 40
        
        img = Image.new('RGB', (width, height), color=(10, 14, 39))
        draw = ImageDraw.Draw(img)
        
        x, y = 20, 20
        for line in lines:
            draw.text((x, y), line, fill=(0, 255, 0), font=None)
            y += char_height
        
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        return img_bytes
    except Exception as e:
        return None

# Main UI
st.title("🎨 ASCII Art Generator")
st.markdown("Transform text and images into stunning ASCII art with professional styling options")

# Sidebar - Settings
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Theme toggle
    theme_options = ["Dark Terminal", "Light Terminal"]
    current_theme_index = 0 if st.session_state.theme == 'dark' else 1
    theme = st.radio("🌓 Theme", theme_options, index=current_theme_index, key="theme_radio")
    st.session_state.theme = 'dark' if theme == "Dark Terminal" else 'light'
    
    st.divider()
    
    # Tab selection
    tab_options = ["Text to ASCII", "Image to ASCII", "Gallery", "Effects"]
    tab = st.radio("Mode", tab_options, horizontal=False, key="tab_radio")

# Main content area
if tab == "Text to ASCII":
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("📝 Input")
        
        text_input = st.text_area(
            "Enter text to convert:",
            placeholder="Type something awesome...",
            height=100
        )
        
        font = st.selectbox(
            "Font Style",
            options=get_pyfiglet_fonts(),
            index=0
        )
        
        alignment = st.radio(
            "Text Alignment",
            ["left", "center", "right"],
            horizontal=True
        )
        
        spacing = st.slider("Letter Spacing", 1, 3, 1)
        
        st.divider()
        
        st.subheader("🎨 Styling")
        
        apply_color = st.checkbox("Apply Colors")
        if apply_color:
            color1 = st.color_picker("Primary Color", "#00ff00")
            gradient_mode = st.checkbox("Gradient Effect")
            if gradient_mode:
                color2 = st.color_picker("Secondary Color", "#ff00ff")
        
        apply_border = st.checkbox("Add Border")
        if apply_border:
            border_style = st.selectbox(
                "Border Style",
                ["single", "double", "rounded", "dashed", "starred", "hash", "equals"]
            )
        
        bg_color = st.color_picker("Background Color", "#0a0e27") if st.checkbox("Custom Background") else None
        
        st.divider()
        
        st.subheader("✨ Effects")
        
        effect = st.selectbox(
            "Visual Effects",
            ["none", "invert", "flip_horizontal", "flip_vertical", "bold"]
        )
        
        density = st.select_slider(
            "Character Density",
            options=["light", "medium", "dense"],
            value="medium"
        )
    
    with col2:
        st.subheader("👁️ Live Preview")
        
        if text_input:
            # Generate ASCII art
            art = generate_ascii_art(text_input, font, alignment, spacing)
            
            # Apply effects
            if effect != "none":
                art = apply_effects(art, effect)
            
            # Add border
            if apply_border:
                art = add_border(art, border_style)
            
            st.session_state.current_art = art
            
            # Apply coloring for display
            if apply_color:
                if gradient_mode:
                    art_display = create_colored_html(art, color1, color2, gradient=True)
                else:
                    art_display = create_colored_html(art, color1)
            else:
                art_display = art
            
            # Display preview
            theme_class = 'light' if st.session_state.theme == 'light' else ''
            st.markdown(
                f'<div class="terminal-output {theme_class}"><pre class="ascii-preview">{art_display}</pre></div>',
                unsafe_allow_html=True
            )
            
            # Statistics
            lines = art.split('\n')
            non_empty_lines = [l for l in lines if l.strip()]
            col1_stat, col2_stat, col3_stat = st.columns(3)
            with col1_stat:
                st.metric("Lines", len(non_empty_lines))
            with col2_stat:
                st.metric("Width", max(len(l) for l in lines) if lines else 0)
            with col3_stat:
                st.metric("Characters", sum(len(l) for l in lines))
            
            # Export options
            st.divider()
            st.subheader("💾 Export")
            
            col_txt, col_html, col_png, col_copy = st.columns(4)
            
            with col_txt:
                txt_data = art.encode('utf-8')
                st.download_button(
                    label="📄 TXT",
                    data=txt_data,
                    file_name="ascii_art.txt",
                    mime="text/plain"
                )
            
            with col_html:
                html_data = export_as_html(art, text_input)
                st.download_button(
                    label="🌐 HTML",
                    data=html_data,
                    file_name="ascii_art.html",
                    mime="text/html"
                )
            
            with col_png:
                png_data = export_as_png(art)
                if png_data:
                    st.download_button(
                        label="🖼️ PNG",
                        data=png_data,
                        file_name="ascii_art.png",
                        mime="image/png"
                    )
            
            with col_copy:
                if st.button("📋 Copy"):
                    st.success("Copied to clipboard! (Use system clipboard)")
            
            # Save to gallery
            st.divider()
            col_name, col_save = st.columns([3, 1])
            with col_name:
                gallery_name = st.text_input("Save to gallery as:", value=text_input[:30])
            with col_save:
                if st.button("💾 Save"):
                    save_to_gallery(gallery_name, art, {
                        'font': font,
                        'alignment': alignment,
                        'spacing': spacing,
                        'effect': effect
                    })
                    st.success(f"Saved as '{gallery_name}'!")
        else:
            st.info("👈 Enter text in the left panel to see the preview")

elif tab == "Image to ASCII":
    st.subheader("🖼️ Image to ASCII Converter")
    
    uploaded_file = st.file_uploader("Upload an image", type=['png', 'jpg', 'jpeg', 'gif', 'bmp'])
    
    if uploaded_file:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Settings")
            width = st.slider("ASCII Width", 40, 200, 80)
            density = st.selectbox("Character Density", ["light", "medium", "dense"])
            invert = st.checkbox("Invert Colors")
        
        with col2:
            st.subheader("Preview")
            
            art = image_to_ascii(uploaded_file, density, width)
            
            if invert:
                art = apply_effects(art, 'invert')
            
            st.session_state.current_art = art
            
            theme_class = 'light' if st.session_state.theme == 'light' else ''
            st.markdown(
                f'<div class="terminal-output {theme_class}"><pre class="ascii-preview">{art}</pre></div>',
                unsafe_allow_html=True
            )
            
            # Export
            st.divider()
            col_txt, col_html, col_copy = st.columns(3)
            
            with col_txt:
                st.download_button(
                    label="📄 Download TXT",
                    data=art.encode('utf-8'),
                    file_name="ascii_image.txt",
                    mime="text/plain"
                )
            
            with col_html:
                html_data = export_as_html(art, "Image ASCII Art")
                st.download_button(
                    label="🌐 Download HTML",
                    data=html_data,
                    file_name="ascii_image.html",
                    mime="text/html"
                )

elif tab == "Gallery":
    st.subheader("🎨 Saved ASCII Art Gallery")
    
    if st.session_state.gallery:
        for i, item in enumerate(st.session_state.gallery):
            with st.expander(f"📌 {item['name']} - {item['timestamp'][:10]}"):
                theme_class = 'light' if st.session_state.theme == 'light' else ''
                st.markdown(
                    f'<div class="terminal-output {theme_class}"><pre class="ascii-preview">{item["art"]}</pre></div>',
                    unsafe_allow_html=True
                )
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.download_button(
                        label="📄 Export",
                        data=item['art'].encode('utf-8'),
                        file_name=f"{item['name']}.txt",
                        mime="text/plain",
                        key=f"download_{i}"
                    )
                
                with col2:
                    if st.button("📋 Load", key=f"load_{i}"):
                        st.session_state.current_art = item['art']
                        st.success("Loaded! Go to 'Text to ASCII' tab")
                
                with col3:
                    if st.button("🗑️ Delete", key=f"delete_{i}"):
                        st.session_state.gallery.pop(i)
                        st.rerun()
    else:
        st.info("No saved artwork yet. Create and save some ASCII art!")

elif tab == "Effects":
    st.subheader("✨ Advanced Effects")
    
    if st.session_state.current_art:
        art = st.session_state.current_art
        
        effect_type = st.selectbox(
            "Choose Effect",
            ["Typewriter Animation", "Wave Animation", "Flicker Animation", "Color Bands"]
        )
        
        if effect_type == "Typewriter Animation":
            speed = st.slider("Speed (ms per char)", 10, 200, 50)
            placeholder = st.empty()
            
            full_art = ""
            for char in art:
                full_art += char
                placeholder.code(full_art, language="")
                time.sleep(speed / 1000)
        
        elif effect_type == "Wave Animation":
            frames = st.slider("Animation Frames", 5, 20, 10)
            
            lines = art.split('\n')
            placeholder = st.empty()
            
            for frame in range(frames):
                wave_art = ""
                for i, line in enumerate(lines):
                    offset = int(2 * math.sin(i / 3 + frame / 5))
                    wave_art += " " * offset + line + "\n"
                
                placeholder.code(wave_art, language="")
                time.sleep(0.2)
        
        elif effect_type == "Flicker Animation":
            frames = st.slider("Animation Frames", 5, 20, 10)
            
            placeholder = st.empty()
            
            for _ in range(frames):
                flicker_art = ""
                for char in art:
                    if char != '\n':
                        flicker_art += char if (ord(char) % 2 == 0) else "█"
                    else:
                        flicker_art += char
                
                placeholder.code(flicker_art, language="")
                time.sleep(0.2)
        
        elif effect_type == "Color Bands":
            colors = st.multiselect(
                "Select Colors",
                ["#00ff00", "#ff00ff", "#00ffff", "#ffff00", "#ff0000", "#0088ff"],
                default=["#00ff00", "#ff00ff", "#00ffff"]
            )
            
            if colors and len(colors) >= 2:
                colored_art = create_colored_html(art, colors[0], colors[1], gradient=True)
                theme_class = 'light' if st.session_state.theme == 'light' else ''
                st.markdown(
                    f'<div class="terminal-output {theme_class}"><pre class="ascii-preview">{colored_art}</pre></div>',
                    unsafe_allow_html=True
                )
            elif colors and len(colors) == 1:
                colored_art = create_colored_html(art, colors[0])
                theme_class = 'light' if st.session_state.theme == 'light' else ''
                st.markdown(
                    f'<div class="terminal-output {theme_class}"><pre class="ascii-preview">{colored_art}</pre></div>',
                    unsafe_allow_html=True
                )
    else:
        st.info("Create some ASCII art first to apply effects!")

# Footer
st.divider()
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 12px; margin-top: 20px;'>
    🎨 ASCII Art Generator | Built with Streamlit | All conversions are client-side
    </div>
    """,
    unsafe_allow_html=True
)
