import io
import os
from PIL import Image, ImageDraw, ImageFont
import streamlit as st

st.set_page_config(page_title="Gerador de Autoassinatura IFSP", layout="centered")
st.title("Gerador de Autoassinatura IFSP")
st.write("Preencha os dados abaixo para gerar a imagem da assinatura.")

BASE_DIR = os.path.dirname(__file__)
TEMPLATE_PATH = os.path.join(BASE_DIR, "assets", "template.jpeg")

# Fontes comuns no Linux/Streamlit Cloud. Se não encontrar, usa fonte padrão.
def font(size, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        "arialbd.ttf" if bold else "arial.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return ImageFont.load_default()

nome = st.text_input("Nome completo", "NOME COMPLETO")
funcao = st.text_input("Função / Cargo", "Função / Cargo")
setor = st.text_input("Departamento / Setor", "Setor / Departamento")
email = st.text_input("E-mail", "seu.nome@ifsp.edu.br")
telefone = st.text_input("Telefone", "(11) 1234-5678")
site = st.text_input("Site", "www.ifsp.edu.br")


def gerar_assinatura():
    img = Image.open(TEMPLATE_PATH).convert("RGB")
    draw = ImageDraw.Draw(img)

    # Apaga somente os textos originais.
    # Importante: não apagar a faixa dos ícones verdes à esquerda dos contatos.
    draw.rectangle((300, 35, 620, 150), fill="white")
    draw.rectangle((350, 155, 625, 275), fill="white")

    azul = (18, 37, 67)
    verde = (47, 151, 57)
    cinza = (65, 65, 65)
    amarelo = (236, 211, 61)

    draw.text((313, 42), nome.upper(), font=font(30, bold=True), fill=azul)
    draw.text((313, 82), funcao, font=font(23), fill=verde)
    draw.text((313, 116), setor, font=font(20), fill=cinza)
    draw.line((307, 148, 522, 148), fill=amarelo, width=2)

    draw.text((352, 165), email, font=font(15), fill=cinza)
    draw.text((352, 210), telefone, font=font(15), fill=cinza)
    draw.text((352, 252), site, font=font(15), fill=cinza)

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
