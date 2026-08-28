"""
Guarda automatizada da REGRA DE OURO do projeto.

O enunciado permite usar NumPy/Pandas para carregar dados e validar
resultados, mas exige que as medidas EXIBIDAS AO USUARIO venham das
funcoes implementadas pela equipe.

E facil violar essa regra sem perceber -- basta alguem escrever um
`df["cnt"].mean()` num ajuste de ultima hora. Estes testes leem o codigo
fonte e falham se isso acontecer.
"""

import ast
import os

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACOTE_NUCLEO = os.path.join(RAIZ, "minhastats")
PASTA_APP = os.path.join(RAIZ, "app")

# O nucleo pode importar SO isto da biblioteca padrao
IMPORTS_PERMITIDOS_NO_NUCLEO = {"math", "random"}

# Metodos estatisticos do pandas/numpy que nao podem aparecer na interface
METODOS_PROIBIDOS_NA_INTERFACE = {
    "mean", "median", "mode", "std", "var", "quantile", "corr", "cov",
    "describe", "skew", "kurt", "kurtosis", "sem", "percentile",
}


def _arquivos_python(pasta):
    for diretorio, _, arquivos in os.walk(pasta):
        if "__pycache__" in diretorio:
            continue
        for arquivo in arquivos:
            if arquivo.endswith(".py"):
                yield os.path.join(diretorio, arquivo)


def _modulos_importados(caminho):
    """Nomes de modulo de todos os import/from-import do arquivo."""
    with open(caminho, encoding="utf-8") as f:
        arvore = ast.parse(f.read(), filename=caminho)

    modulos = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            for alias in no.names:
                modulos.add(alias.name.split(".")[0])
        elif isinstance(no, ast.ImportFrom):
            if no.level == 0 and no.module:  # ignora imports relativos
                modulos.add(no.module.split(".")[0])
    return modulos


@pytest.mark.parametrize(
    "caminho", sorted(_arquivos_python(PACOTE_NUCLEO)),
    ids=lambda c: os.path.basename(c),
)
def test_nucleo_nao_importa_biblioteca_externa(caminho):
    """minhastats/ so pode importar `math` e `random`."""
    proibidos = _modulos_importados(caminho) - IMPORTS_PERMITIDOS_NO_NUCLEO
    assert not proibidos, (
        f"{os.path.relpath(caminho, RAIZ)} importa {sorted(proibidos)}. "
        f"O nucleo estatistico deve usar apenas {sorted(IMPORTS_PERMITIDOS_NO_NUCLEO)} "
        f"-- numpy/scipy/pandas/statistics so podem aparecer em tests/."
    )


@pytest.mark.parametrize(
    "caminho", sorted(_arquivos_python(PASTA_APP)),
    ids=lambda c: os.path.basename(c),
)
def test_interface_nao_chama_estatistica_do_pandas(caminho):
    """Nenhuma chamada do tipo `algo.mean()` / `algo.corr()` na interface.

    Percorre a AST procurando chamadas a metodos com nome proibido. O
    pandas pode ser usado para LER e ORGANIZAR (read_csv, map, tolist,
    nunique, isna), mas nao para CALCULAR o que aparece na tela.
    """
    with open(caminho, encoding="utf-8") as f:
        arvore = ast.parse(f.read(), filename=caminho)

    encontrados = []
    for no in ast.walk(arvore):
        if isinstance(no, ast.Call) and isinstance(no.func, ast.Attribute):
            if no.func.attr in METODOS_PROIBIDOS_NA_INTERFACE:
                encontrados.append(f"linha {no.lineno}: .{no.func.attr}()")

    assert not encontrados, (
        f"{os.path.relpath(caminho, RAIZ)} chama método estatístico de "
        f"biblioteca: {encontrados}. Use minhastats."
    )


def test_app_principal_tambem_respeita_a_regra():
    """O proprio app.py, na raiz do projeto."""
    caminho = os.path.join(RAIZ, "app.py")
    with open(caminho, encoding="utf-8") as f:
        arvore = ast.parse(f.read(), filename=caminho)

    for no in ast.walk(arvore):
        if isinstance(no, ast.Call) and isinstance(no.func, ast.Attribute):
            assert no.func.attr not in METODOS_PROIBIDOS_NA_INTERFACE, (
                f"app.py linha {no.lineno} chama .{no.func.attr}()"
            )


def test_nucleo_e_importavel_sem_nenhuma_dependencia_externa():
    """Sanidade final: importar minhastats num interpretador onde numpy,
    scipy e pandas foram bloqueados deve funcionar."""
    import subprocess
    import sys

    codigo = (
        "import sys\n"
        "for proibido in ('numpy', 'scipy', 'pandas', 'statistics'):\n"
        "    sys.modules[proibido] = None\n"
        "import minhastats\n"
        "assert minhastats.media([1, 2, 3]) == 2.0\n"
        # comparacao com folga: em ponto flutuante r sai 0.9999999999999998,
        # e nao exatamente 1.0 -- o proprio teste flagrou isso
        "assert abs(minhastats.correlacao_pearson([1, 2, 3], [2, 4, 6]) - 1.0) < 1e-12\n"
        "print('OK')\n"
    )
    resultado = subprocess.run(
        [sys.executable, "-c", codigo], cwd=RAIZ,
        capture_output=True, text=True,
    )
    assert resultado.returncode == 0, (
        f"minhastats nao carregou sem as bibliotecas externas:\n{resultado.stderr}"
    )
    assert "OK" in resultado.stdout
