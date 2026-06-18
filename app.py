import io
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import streamlit as st

st.set_page_config(page_title="Gerador de Autoassinatura IFSP", layout="centered")
st.title("Gerador de Autoassinatura IFSP")
st.write("Preencha os dados abaixo para gerar a imagem da assinatura.")

BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_PATH = BASE_DIR / "assets" / "template.jpeg"

# Versão pensada para funcionar igual no Windows e no Streamlit Cloud.
# O problema da fonte pequena no site acontece quando o PIL não encontra uma fonte TTF
# e cai na fonte padrão. Aqui a busca é mais ampla e prioriza fontes com acentuação.
def localizar_fonte(bold: bool = False) -> str | None:
    nomes = (
        ["DejaVuSans-Bold.ttf", "Arial Bold.ttf", "arialbd.ttf", "LiberationSans-Bold.ttf", "NotoSans-Bold.ttf"]
        if bold
        else ["DejaVuSans.ttf", "Arial.ttf", "arial.ttf", "LiberationSans-Regular.ttf", "NotoSans-Regular.ttf"]
    )

    pastas = [
        Path("C:/Windows/Fonts"),
        Path("/usr/share/fonts"),
        Path("/usr/local/share/fonts"),
        Path("/System/Library/Fonts"),
        Path("/Library/Fonts"),
    ]

    # 1) Caminhos diretos e recursivos
    for pasta in pastas:
        if not pasta.exists():
            continue
        for nome in nomes:
            direto = pasta / nome
            if direto.exists():
                return str(direto)
        try:
            for arquivo in pasta.rglob("*.ttf"):
                if arquivo.name in nomes:
                    return str(arquivo)
        except Exception:
            pass

    # 2) Nomes genéricos, caso o Pillow consiga resolver sozinho
    for nome in nomes:
        try:
            ImageFont.truetype(nome, 20)
            return nome
        except Exception:
            pass
    return None

FONTE_REGULAR = localizar_fonte(False)
FONTE_BOLD = localizar_fonte(True) or FONTE_REGULAR


def fonte(tamanho: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    caminho = FONTE_BOLD if bold else FONTE_REGULAR
    if caminho:
        try:
            return ImageFont.truetype(caminho, tamanho)
        except Exception:
            pass
    return ImageFont.load_default()


def largura_texto(draw: ImageDraw.ImageDraw, texto: str, fnt) -> int:
    bbox = draw.textbbox((0, 0), texto, font=fnt)
    return bbox[2] - bbox[0]


def fonte_ajustada(draw: ImageDraw.ImageDraw, texto: str, largura_max: int, inicial: int, minimo: int, bold: bool = False):
    for tamanho in range(inicial, minimo - 1, -1):
        fnt = fonte(tamanho, bold=bold)
        if largura_texto(draw, texto, fnt) <= largura_max:
            return fnt
    return fonte(minimo, bold=bold)


nome = st.text_input("Nome completo", "CAIO ITALO MARCIERI PIMPINATO")
funcao = st.text_input("Função / Cargo", "Aluno")
setor = st.text_input("Departamento / Setor", "DEL / Campus São Paulo")
email = st.text_input("E-mail", "caio.pimpinato@aluno.ifsp.edu.br")
telefone = st.text_input("Telefone", "(11) 986767015")
site = st.text_input("Site", "www.ifsp.edu.br")


def gerar_assinatura():
    img = Image.open(TEMPLATE_PATH).convert("RGB")
    draw = ImageDraw.Draw(img)

    # Limpa somente as áreas de texto do modelo, sem apagar ícones nem logotipo.
    draw.rectangle((300, 25, 845, 154), fill="white")
    draw.rectangle((350, 158, 735, 276), fill="white")

    azul = (18, 37, 67)
    verde = (0, 150, 57)
    cinza = (60, 60, 60)
    amarelo = (236, 211, 61)

    # Disposição com fontes grandes, próxima ao modelo aprovado.
    nome_final = nome.upper().strip()
    draw.text((313, 42), nome_final, font=fonte_ajustada(draw, nome_final, 535, 34, 24, bold=True), fill=azul)
    draw.text((313, 84), funcao.strip(), font=fonte_ajustada(draw, funcao.strip(), 330, 26, 20), fill=verde)
    draw.text((313, 119), setor.strip(), font=fonte_ajustada(draw, setor.strip(), 350, 22, 17), fill=cinza)
    draw.line((307, 150, 522, 150), fill=amarelo, width=2)

    draw.text((352, 166), email.strip(), font=fonte_ajustada(draw, email.strip(), 365, 16, 12), fill=cinza)
    draw.text((352, 211), telefone.strip(), font=fonte_ajustada(draw, telefone.strip(), 315, 16, 12), fill=cinza)
    draw.text((352, 253), site.strip(), font=fonte_ajustada(draw, site.strip(), 315, 16, 12), fill=cinza)

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

with st.expander("Diagnóstico de fonte"):
    st.write("Fonte regular:", FONTE_REGULAR or "não encontrada")
    st.write("Fonte negrito:", FONTE_BOLD or "não encontrada")
