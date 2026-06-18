import io
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import streamlit as st

st.set_page_config(page_title="Gerador de Autoassinatura IFSP", layout="centered")
st.title("Gerador de Autoassinatura IFSP")
st.write("Preencha os dados abaixo para gerar a imagem da assinatura.")

BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_PATH = BASE_DIR / "assets" / "template.jpeg"
FONTS_DIR = BASE_DIR / "assets" / "fonts"

# IMPORTANTE PARA O STREAMLIT CLOUD:
# Coloque os arquivos de fonte dentro de assets/fonts/ no GitHub.
# O código abaixo procura primeiro pelas fontes do projeto, antes de tentar fontes do sistema.
def localizar_fonte(bold: bool = False) -> str | None:
    nomes_locais = (
        [
            "Montserrat-ExtraBold.ttf",
            "Montserrat-Bold.ttf",
            "Montserrat-SemiBold.ttf",
            "Montserrat-Bold.otf",
            "Montserrat-SemiBold.otf",
            "arialbd.ttf",
            "Arial Bold.ttf",
            "NotoSans-Bold.ttf",
            "DejaVuSans-Bold.ttf",
        ]
        if bold
        else [
            "Montserrat-SemiBold.ttf",
            "Montserrat-Medium.ttf",
            "Montserrat-Regular.ttf",
            "Montserrat-Regular.otf",
            "Montserrat-Medium.otf",
            "arial.ttf",
            "Arial.ttf",
            "NotoSans-Regular.ttf",
            "DejaVuSans.ttf",
        ]
    )

    # 1) Primeiro procura em assets/fonts, que é o jeito correto no Streamlit Cloud.
    if FONTS_DIR.exists():
        for nome in nomes_locais:
            caminho = FONTS_DIR / nome
            if caminho.exists():
                return str(caminho)

        # Caso o Windows copie com outro nome, tenta achar por palavras-chave.
        try:
            arquivos = list(FONTS_DIR.rglob("*.ttf")) + list(FONTS_DIR.rglob("*.otf"))
            for arquivo in arquivos:
                n = arquivo.name.lower()
                if "montserrat" in n:
                    if bold and ("bold" in n or "semibold" in n or "extrabold" in n):
                        return str(arquivo)
                    if not bold and ("regular" in n or "medium" in n):
                        return str(arquivo)
        except Exception:
            pass

    # 2) Depois tenta fontes comuns do sistema local ou Linux do Streamlit.
    nomes_sistema = (
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

    for pasta in pastas:
        if not pasta.exists():
            continue
        for nome in nomes_sistema:
            direto = pasta / nome
            if direto.exists():
                return str(direto)
        try:
            for arquivo in pasta.rglob("*.ttf"):
                if arquivo.name in nomes_sistema:
                    return str(arquivo)
        except Exception:
            pass

    # 3) Última tentativa: deixar o Pillow resolver pelo nome.
    for nome in nomes_sistema:
        try:
            ImageFont.truetype(nome, 20)
            return nome
        except Exception:
            pass

    return None


FONTE_REGULAR = localizar_fonte(False)
FONTE_BOLD = localizar_fonte(True) or FONTE_REGULAR


def fonte(tamanho: int, bold: bool = False):
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
    texto = texto or ""
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

    # Limpa apenas os textos do template, preservando ícones, logotipo e barras coloridas.
    draw.rectangle((300, 25, 850, 154), fill="white")
    draw.rectangle((350, 158, 740, 276), fill="white")

    azul = (18, 37, 67)
    verde = (0, 150, 57)
    cinza = (60, 60, 60)
    amarelo = (236, 211, 61)

    nome_final = nome.upper().strip()
    funcao_final = funcao.strip()
    setor_final = setor.strip()
    email_final = email.strip()
    telefone_final = telefone.strip()
    site_final = site.strip()

    # Layout com fonte grande, igual ao modelo aprovado.
    draw.text((313, 38), nome_final, font=fonte_ajustada(draw, nome_final, 540, 48, 34, bold=True), fill=azul)
    draw.text((313, 88), funcao_final, font=fonte_ajustada(draw, funcao_final, 340, 30, 22, bold=False), fill=verde)
    draw.text((313, 122), setor_final, font=fonte_ajustada(draw, setor_final, 380, 24, 18, bold=False), fill=cinza)
    draw.line((307, 150, 522, 150), fill=amarelo, width=2)

    draw.text((352, 166), email_final, font=fonte_ajustada(draw, email_final, 365, 18, 14), fill=cinza)
    draw.text((352, 211), telefone_final, font=fonte_ajustada(draw, telefone_final, 315, 18, 14), fill=cinza)
    draw.text((352, 253), site_final, font=fonte_ajustada(draw, site_final, 315, 18, 14), fill=cinza)

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
    st.write("Pasta de fontes esperada:", str(FONTS_DIR))
    st.write("Fonte regular:", FONTE_REGULAR or "não encontrada")
    st.write("Fonte negrito:", FONTE_BOLD or "não encontrada")
    st.write("Arquivos encontrados em assets/fonts:")
    if FONTS_DIR.exists():
        encontrados = [p.name for p in FONTS_DIR.rglob("*") if p.is_file()]
        st.write(encontrados if encontrados else "nenhum arquivo encontrado")
    else:
        st.write("pasta assets/fonts não existe")
