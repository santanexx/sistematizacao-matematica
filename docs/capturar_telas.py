"""
Utilitario para gerar as capturas de tela do README.

Sobe um navegador (Chrome do sistema, via Playwright), percorre cada
modulo da aplicacao e salva um PNG em docs/imagens/.

Uso:
    # terminal 1
    streamlit run app.py --server.port 8599
    # terminal 2
    python docs/capturar_telas.py

Dependencia extra (nao necessaria para rodar a aplicacao):
    pip install playwright
"""

import os
import sys

from playwright.sync_api import sync_playwright

URL = os.environ.get("URL_APP", "http://localhost:8599")
DESTINO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imagens")

# (rotulo no menu lateral, prefixo do arquivo, posicoes de rolagem)
# O Streamlit rola dentro de um container proprio, entao `full_page` nao
# captura a pagina inteira: rolamos e capturamos a viewport em posicoes
# diferentes.
TELAS = [
    ("Módulo 0", "modulo0_dados", [0]),
    ("Módulo 1", "modulo1_nucleo", [0, 1400, 2800]),
    ("Módulo 2", "modulo2_descritiva", [0, 1400, 2900]),
    ("Módulo 3", "modulo3_simulacao", [0, 1300]),
    ("Módulo 4", "modulo4_distribuicoes", [0, 1200]),
    ("Módulo 5", "modulo5_regressao", [0, 1300]),
    ("Módulo 6", "modulo6_descobertas", [0, 1700]),
]


def capturar():
    os.makedirs(DESTINO, exist_ok=True)

    with sync_playwright() as p:
        navegador = p.chromium.launch(channel="chrome")
        pagina = navegador.new_page(
            viewport={"width": 1600, "height": 1400},
            color_scheme="light",  # tema claro fica melhor no README
            device_scale_factor=1.25,
        )
        pagina.goto(URL, wait_until="networkidle", timeout=90000)
        pagina.wait_for_timeout(8000)

        for rotulo, prefixo, rolagens in TELAS:
            pagina.locator(f"label:has-text('{rotulo}')").first.click()
            pagina.wait_for_timeout(10000)  # espera o modulo terminar de calcular

            for indice, deslocamento in enumerate(rolagens, start=1):
                pagina.evaluate(
                    """(y) => {
                        const alvos = [
                            document.querySelector('section.main'),
                            document.querySelector('[data-testid="stMain"]'),
                            document.querySelector('[data-testid="stAppViewContainer"]'),
                            document.scrollingElement,
                        ].filter(Boolean);
                        for (const el of alvos) { el.scrollTop = y; }
                        window.scrollTo(0, y);
                    }""",
                    deslocamento,
                )
                pagina.wait_for_timeout(2500)

                sufixo = "" if len(rolagens) == 1 else f"_{indice}"
                arquivo = f"{prefixo}{sufixo}.png"
                caminho = os.path.join(DESTINO, arquivo)
                pagina.screenshot(path=caminho)
                print(f"  - {arquivo} ({os.path.getsize(caminho) // 1024} KB)")

        navegador.close()


if __name__ == "__main__":
    print(f"Capturando telas de {URL} ...")
    try:
        capturar()
    except Exception as erro:
        print(f"Falha: {erro}", file=sys.stderr)
        sys.exit(1)
    print(f"Imagens salvas em {DESTINO}")
