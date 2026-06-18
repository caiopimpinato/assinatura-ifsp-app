import io
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
import streamlit as st


st.set_page_config(page_title="Gerador de Autoassinatura IFSP", layout="centered")
st.title("Gerador de Autoassinatura IFSP")
st.write("Preencha os dados abaixo para gerar a imagem da assinatura.")

BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_PATH = BASE_DIR / "assets" / "template.jpeg"

# O correto no GitHub é assets/fonts, mas deixei fallback para assets/Fonts
# caso a pasta tenha sido enviada com F maiúsculo.
FONTS_DIRS = [
    BASE_DIR / "assets" / "fonts",
    BASE_DIR / "assets" / "Fonts",
]


def arquivos_de_fontes():
    arquivos = []
    for pasta in FONTS_DIRS:
        if pasta.exists():
            arquivos.extend(list(pasta.rglob("*.ttf")))
            arquivos.extend(list(pasta.rglob("*.otf")))
    return arquivos


def localizar_fonte(preferencias: list[str]) -> str | None:
    arquivos = arquivos_de_fontes()

    mapa = {a.name.lower(): a for a in arquivos}
    for nome in preferencias:
        achado = mapa.get(nome.lower())
        if achado:
            return str(achado)

    for nome in preferencias:
        chave = (
            nome.lower()
            .replace(".ttf", "")
            .replace(".otf", "")
            .replace("-", "")
            .replace("_", "")
            .replace(" ", "")
        )
        for arquivo in arquivos:
            n = (
                arquivo.name.lower()
                .replace(".ttf", "")
                .replace(".otf", "")
                .replace("-", "")
                .replace("_", "")
                .replace(" ", "")
            )
            if chave in n:
                return str(arquivo)

    pastas_sistema = [
        Path("C:/Windows/Fonts"),
        Path("/usr/share/fonts"),
        Path("/usr/local/share/fonts"),
        Path("/System/Library/Fonts"),
        Path("/Library/Fonts"),
    ]

    for pasta in pastas_sistema:
        if not pasta.exists():
            continue
        for nome in preferencias:
            direto = pasta / nome
            if direto.exists():
                return str(direto)
        try:
            for arquivo in pasta.rglob("*.ttf"):
                for nome in preferencias:
                    if arquivo.name.lower() == nome.lower():
                        return str(arquivo)
        except Exception:
            pass

    for nome in preferencias:
        try:
            ImageFont.truetype(nome, 20)
            return nome
        except Exception:
            pass

    return None


FONTE_NOME = localizar_fonte([
    "Montserrat-ExtraBold.ttf",
    "Montserrat-Black.ttf",
    "Montserrat-Bold.ttf",
    "Montserrat-SemiBold.ttf",
    "arialbd.ttf",
    "DejaVuSans-Bold.ttf",
])

FONTE_CARGO = localizar_fonte([
    "Montserrat-SemiBold.ttf",
    "Montserrat-Bold.ttf",
    "Montserrat-Medium.ttf",
    "arialbd.ttf",
    "DejaVuSans-Bold.ttf",
])

FONTE_SETOR = localizar_fonte([
    "Montserrat-Medium.ttf",
    "Montserrat-SemiBold.ttf",
    "Montserrat-Regular.ttf",
    "arial.ttf",
    "DejaVuSans.ttf",
])

FONTE_CONTATO = localizar_fonte([
    "Montserrat-Medium.ttf",
    "Montserrat-SemiBold.ttf",
    "Montserrat-Regular.ttf",
    "arial.ttf",
    "DejaVuSans.ttf",
])

FONTE_NOME = FONTE_NOME or FONTE_CARGO or FONTE_SETOR or FONTE_CONTATO
FONTE_CARGO = FONTE_CARGO or FONTE_NOME or FONTE_SETOR or FONTE_CONTATO
FONTE_SETOR = FONTE_SETOR or FONTE_CARGO or FONTE_NOME or FONTE_CONTATO
FONTE_CONTATO = FONTE_CONTATO or FONTE_SETOR or FONTE_CARGO or FONTE_NOME


def carregar_fonte(caminho: str | None, tamanho: int):
    if caminho:
        try:
            return ImageFont.truetype(caminho, tamanho)
        except Exception:
            pass
    return ImageFont.load_default()


def largura_texto(draw: ImageDraw.ImageDraw, texto: str, fnt) -> int:
    bbox = draw.textbbox((0, 0), texto, font=fnt)
    return bbox[2] - bbox[0]


def fonte_ajustada(draw: ImageDraw.ImageDraw, texto: str, largura_max: int, inicial: int, minimo: int, caminho_fonte: str | None):
    texto = texto or ""
    for tamanho in range(inicial, minimo - 1, -1):
        fnt = carregar_fonte(caminho_fonte, tamanho)
        if largura_texto(draw, texto, fnt) <= largura_max:
            return fnt
    return carregar_fonte(caminho_fonte, minimo)


nome = st.text_input("Nome completo", "CAIO ITALO MARCIERI PIMPINATO")
funcao = st.text_input("Função / Cargo", "Aluno")
setor = st.text_input("Departamento / Setor", "DEL / Campus São Paulo")
email = st.text_input("E-mail", "caio.pimpinato@aluno.ifsp.edu.br")
telefone = st.text_input("Telefone", "(11) 986767015")
site = st.text_input("Site", "www.ifsp.edu.br")


def gerar_assinatura():
    img = Image.open(TEMPLATE_PATH).convert("RGB")
    draw = ImageDraw.Draw(img)

    draw.rectangle((300, 25, 855, 154), fill="white")
    draw.rectangle((350, 158, 745, 276), fill="white")

    azul = (18, 37, 67)
    verde = (0, 150, 57)
    cinza = (45, 45, 45)
    amarelo = (236, 211, 61)

    nome_final = nome.upper().strip()
    funcao_final = funcao.strip()
    setor_final = setor.strip()
    email_final = email.strip()
    telefone_final = telefone.strip()
    site_final = site.strip()

    fonte_nome = fonte_ajustada(draw, nome_final, 540, 34, 24, FONTE_NOME)
    fonte_cargo = fonte_ajustada(draw, funcao_final, 330, 25, 19, FONTE_CARGO)
    fonte_setor = fonte_ajustada(draw, setor_final, 350, 21, 16, FONTE_SETOR)
    fonte_email = fonte_ajustada(draw, email_final, 365, 16, 12, FONTE_CONTATO)
    fonte_telefone = fonte_ajustada(draw, telefone_final, 315, 16, 12, FONTE_CONTATO)
    fonte_site = fonte_ajustada(draw, site_final, 315, 16, 12, FONTE_CONTATO)

    draw.text((313, 42), nome_final, font=fonte_nome, fill=azul)
    draw.text((313, 84), funcao_final, font=fonte_cargo, fill=verde)
    draw.text((313, 119), setor_final, font=fonte_setor, fill=cinza)
    draw.line((307, 150, 522, 150), fill=amarelo, width=2)

    draw.text((352, 166), email_final, font=fonte_email, fill=cinza)
    draw.text((352, 211), telefone_final, font=fonte_telefone, fill=cinza)
    draw.text((352, 253), site_final, font=fonte_site, fill=cinza)

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
    st.write("Pastas de fontes procuradas:")
    for pasta in FONTS_DIRS:
        st.write(str(pasta))

    st.write("Fonte do nome:", FONTE_NOME or "não encontrada")
    st.write("Fonte do cargo:", FONTE_CARGO or "não encontrada")
    st.write("Fonte do setor:", FONTE_SETOR or "não encontrada")
    st.write("Fonte dos contatos:", FONTE_CONTATO or "não encontrada")

    st.write("Arquivos encontrados em assets/fonts ou assets/Fonts:")
    encontrados = [str(p.relative_to(BASE_DIR)) for p in arquivos_de_fontes()]
    st.write(encontrados if encontrados else "nenhum arquivo encontrado")
