# Gerador de Autoassinatura IFSP

Sistema simples em Python/Streamlit para gerar uma imagem de autoassinatura a partir de um modelo.

## Como rodar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Como hospedar no GitHub + Streamlit Cloud

1. Crie um repositório no GitHub.
2. Envie estes arquivos para o repositório:
   - `app.py`
   - `requirements.txt`
   - pasta `assets/` com `template.jpeg`
3. Acesse o Streamlit Cloud.
4. Clique em **New app**.
5. Selecione o repositório.
6. Em **Main file path**, coloque:

```text
app.py
```

7. Clique em **Deploy**.

Observação: o GitHub Pages não executa Python. Para hospedar esse sistema gratuitamente, use Streamlit Cloud, Render, Railway ou Hugging Face Spaces.
