import io
import os
from PIL import Image, ImageDraw, ImageFont
import streamlit as st

st.set_page_config(page_title="Gerador de Autoassinatura IFSP", layout="centered")
st.title("Gerador de Autoassinatura IFSP")
st.write("Preencha os dados abaixo para gerar a imagem da assinatura.")

BASE_DIR = os.path.dirname(__file__)
TEMPLATE_PATH = os.path.join(BASE_DIR, "assets", "template.jpeg")

# Busca fontes reais no Windows, Linux/Streamlit Cloud e macOS.
# Isso evita cair na fonte padrão minúscula do PIL.
def font(size, bold=False):
    candidates = [
        # Windows
        r"C:\\Windows\\Fonts\\arialbd.ttf" if bold else r"C:\\Windows\\Fonts\\arial.ttf",
        r"C:\\Windows\\Fonts\\calibrib.ttf" if bold else r"C:\\Windows\\Fonts\\calibri.ttf",
        r"C:\\Windows\\Fonts\\segoeuib.ttf" if bold else r"C:\\Windows\\Fonts\\segoeui.ttf",
        # Linux / Streamlit Cloud
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        # macOS
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
        # nomes genéricos, caso o PIL encontre no sistema
        "arialbd.ttf" if bold else "arial.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return ImageFont.load_default()


def fit_font(text, max_width, start_size, min_size=18, bold=False):
    """Reduz a fonte apenas se o texto for grande demais para caber."""
    dummy = Image.new("RGB", (10, 10))
    d = ImageDraw.Draw(dummy)
    for size in range(start_size, min_size - 1, -1):
        f = font(size, bold=bold)
        bbox = d.textbbox((0, 0), text, font=f)
        if bbox[2] - bbox[0] <= max_width:
            return f
    return font(min_size, bold=bold)

nome = st.text_input("Nome completo", "CAIO ITALO MARCIERI PIMPINATO")
funcao = st.text_input("Função / Cargo", "Aluno")
setor = st.text_input("Departamento / Setor", "DEL")
email = st.text_input("E-mail", "caio.pimpinato@aluno.ifsp.edu.br")
telefone = st.text_input("Telefone", "(11) 986767015")
site = st.text_input("Site", "www.ifsp.edu.br")


def gerar_assinatura():
    img = Image.open(TEMPLATE_PATH).convert("RGB")
    draw = ImageDraw.Draw(img)

    # Limpa somente as áreas de texto do modelo, preservando os ícones e o logo.
    draw.rectangle((300, 30, 835, 152), fill="white")
    draw.rectangle((350, 156, 720, 282), fill="white")

    azul = (18, 37, 67)
    verde = (0, 150, 57)
    cinza = (60, 60, 60)
    amarelo = (236, 211, 61)

    # Layout ampliado, igual ao modelo de referência.
    draw.text((313, 42), nome.upper(), font=fit_font(nome.upper(), 520, 34, 24, bold=True), fill=azul)
    draw.text((313, 84), funcao, font=fit_font(funcao, 300, 26, 20), fill=verde)
    draw.text((313, 119), setor, font=fit_font(setor, 300, 22, 18), fill=cinza)
    draw.line((307, 150, 522, 150), fill=amarelo, width=2)

    # Contatos alinhados com os ícones verdes.
    draw.text((352, 166), email, font=fit_font(email, 360, 16, 12), fill=cinza)
    draw.text((352, 211), telefone, font=fit_font(telefone, 300, 16, 12), fill=cinza)
    draw.text((352, 253), site, font=fit_font(site, 300, 16, 12), fill=cinza)

    return img

assinatura = gerar_assinatura()
st.image(assinatura, caption="Prévia da assinatura", use_container_width=True)

buffer = io.BytesIO()
assinatura.save(buffer, format="PNG")
st.download_button(
    "Baixar assinatura em PNG",
    data=buffer.getvalue(),
    file_name="autoassinatura_ifsp.png",
    mime="image/png",
)
