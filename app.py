import io
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import streamlit as st

st.set_page_config(page_title="Gerador de Autoassinatura IFSP", layout="centered")
st.title("Gerador de Autoassinatura IFSP")
st.write("Preencha os dados abaixo para gerar a imagem da assinatura.")

BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_PATH = BASE_DIR / "assets" / "template.jpeg"

# Aceita tanto assets/fonts quanto assets/Fonts, para evitar erro de maiúsculas/minúsculas no Streamlit Cloud.
FONTS_DIRS = [
    BASE_DIR / "assets" / "fonts",
    BASE_DIR / "assets" / "Fonts",
]


def localizar_fonte(preferencias: list[str]) -> str | None:
    """Procura uma fonte no projeto e depois no sistema."""
    for pasta in FONTS_DIRS:
        if not pasta.exists():
            continue

        # Primeiro tenta nomes exatos.
        for nome in preferencias:
            caminho = pasta / nome
            if caminho.exists():
                return str(caminho)

        # Depois tenta uma busca mais flexível.
        try:
            arquivos = list(pasta.rglob("*.ttf")) + list(pasta.rglob("*.otf"))
            for preferida in preferencias:
                alvo = preferida.lower().replace("-", "").replace("_", "").replace(" ", "")
                for arquivo in arquivos:
                    nome_arquivo = arquivo.name.lower().replace("-", "").replace("_", "").replace(" ", "")
                    if alvo in nome_arquivo:
                        return str(arquivo)
        except Exception:
            pass

    # Fallbacks do sistema local/Linux.
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
            caminho = pasta / nome
            if caminho.exists():
                return str(caminho)
        try:
            for arquivo in pasta.rglob("*.ttf"):
                if arquivo.name in preferencias:
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
    "DejaVuSans-Bold.ttf",
    "arialbd.ttf",
])

FONTE_TEXTO_FORTE = localizar_fonte([
    "Montserrat-SemiBold.ttf",
    "Montserrat-Bold.ttf",
    "Montserrat-Medium.ttf",
    "DejaVuSans-Bold.ttf",
    "arialbd.ttf",
])

FONTE_TEXTO = localizar_fonte([
    "Montserrat-Medium.ttf",
    "Montserrat-SemiBold.ttf",
    "Montserrat-Regular.ttf",
    "DejaVuSans.ttf",
    "arial.ttf",
])

# Fallback final.
FONTE_NOME = FONTE_NOME or FONTE_TEXTO_FORTE or FONTE_TEXTO
FONTE_TEXTO_FORTE = FONTE_TEXTO_FORTE or FONTE_NOME or FONTE_TEXTO
FONTE_TEXTO = FONTE_TEXTO or FONTE_TEXTO_FORTE or FONTE_NOME


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


def desenhar_texto_forte(draw, pos, texto, fonte, cor):
    """
    Reforça visualmente o nome sem depender apenas do peso da fonte.
    Desenha uma cópia deslocada 1 px para dar efeito de negrito.
    """
    x, y = pos
    draw.text((x, y), texto, font=fonte, fill=cor)
    draw.text((x + 1, y), texto, font=fonte, fill=cor)


def desenhar_texto_centralizado_vertical(draw, x, centro_y, texto, fonte, cor):
    """Alinha o texto pelo centro vertical dos ícones."""
    bbox = draw.textbbox((0, 0), texto, font=fonte)
    altura = bbox[3] - bbox[1]
    y = int(centro_y - altura / 2 - bbox[1])
    draw.text((x, y), texto, font=fonte, fill=cor)


# Campos começam vazios para uso por outras pessoas.
nome = st.text_input("Nome completo", "", key="nome_vazio")
funcao = st.text_input("Função / Cargo", "", key="funcao_vazio")
setor = st.text_input("Departamento / Setor", "", key="setor_vazio")
email = st.text_input("E-mail", "", key="email_vazio")
telefone = st.text_input("Telefone", "", key="telefone_vazio")
site = st.text_input("Site", "", key="site_vazio")


def gerar_assinatura():
    img = Image.open(TEMPLATE_PATH).convert("RGB")
    draw = ImageDraw.Draw(img)

    # Limpa os textos e também apaga a linha amarela original do template.
    # Mantém ícones, logotipo e barras coloridas.
    draw.rectangle((300, 20, 870, 156), fill="white")
    draw.rectangle((350, 158, 750, 276), fill="white")

    azul = (18, 37, 67)
    verde = (0, 150, 57)
    cinza = (60, 60, 60)

    nome_final = nome.upper().strip()
    funcao_final = funcao.strip()
    setor_final = setor.strip()
    email_final = email.strip()
    telefone_final = telefone.strip()
    site_final = site.strip()

    # Fontes mais fortes e maiores.
    fonte_nome = fonte_ajustada(draw, nome_final, 560, 56, 36, FONTE_NOME)
    fonte_funcao = fonte_ajustada(draw, funcao_final, 360, 30, 22, FONTE_TEXTO_FORTE)
    fonte_setor = fonte_ajustada(draw, setor_final, 390, 24, 18, FONTE_TEXTO)
    fonte_email = fonte_ajustada(draw, email_final, 365, 18, 13, FONTE_TEXTO)
    fonte_telefone = fonte_ajustada(draw, telefone_final, 315, 18, 13, FONTE_TEXTO)
    fonte_site = fonte_ajustada(draw, site_final, 315, 18, 13, FONTE_TEXTO)

    # Bloco principal sem linha amarela.
    if nome_final:
        desenhar_texto_forte(draw, (313, 34), nome_final, fonte_nome, azul)
    if funcao_final:
        draw.text((313, 90), funcao_final, font=fonte_funcao, fill=verde)
    if setor_final:
        draw.text((313, 124), setor_final, font=fonte_setor, fill=cinza)

    # Contatos alinhados verticalmente com os ícones.
    # Centros aproximados dos ícones no template original.
    if email_final:
        desenhar_texto_centralizado_vertical(draw, 352, 174, email_final, fonte_email, cinza)
    if telefone_final:
        desenhar_texto_centralizado_vertical(draw, 352, 218, telefone_final, fonte_telefone, cinza)
    if site_final:
        desenhar_texto_centralizado_vertical(draw, 352, 260, site_final, fonte_site, cinza)

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
    st.write("Pastas de fontes esperadas:", [str(p) for p in FONTS_DIRS])
    st.write("Fonte do nome:", FONTE_NOME or "não encontrada")
    st.write("Fonte de texto forte:", FONTE_TEXTO_FORTE or "não encontrada")
    st.write("Fonte de texto:", FONTE_TEXTO or "não encontrada")
    st.write("Arquivos encontrados nas pastas de fontes:")
    encontrados = []
    for pasta in FONTS_DIRS:
        if pasta.exists():
            encontrados.extend([str(p.relative_to(BASE_DIR)) for p in pasta.rglob("*") if p.is_file()])
    st.write(encontrados if encontrados else "nenhum arquivo encontrado")
