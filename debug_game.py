#!/usr/bin/env python3
"""
Script de debug para analisar todo o projeto Python
e identificar possíveis problemas ou métodos incompletos.
"""

import ast
import os
import sys
import glob

def analisar_arquivo(caminho_arquivo):
    """Analisar um arquivo Python específico para detectar problemas"""

    if not os.path.exists(caminho_arquivo):
        print(f"❌ Arquivo {caminho_arquivo} não encontrado!")
        return None

    nome_arquivo = os.path.basename(caminho_arquivo)
    print(f"\n🔍 ANÁLISE DE {nome_arquivo.upper()}")
    print("=" * 50)

    # Ler o arquivo
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            conteudo = f.read()
    except OSError as e:
        print(f"❌ Erro ao ler arquivo: {e}")
        return None

    # Parse AST
    try:
        arvore = ast.parse(conteudo)
        print("✅ Sintaxe válida")
    except SyntaxError as e:
        print(f"❌ Erro de sintaxe: {e}")
        return None
    # Encontrar métodos vazios ou incompletos
    metodos_vazios = []
    metodos_incompletos = []
    classes = []
    for node in ast.walk(arvore):
        if isinstance(node, ast.ClassDef):
            classes.append(node.name)
        elif isinstance(node, ast.FunctionDef):
            # Verificar se o método está vazio ou só tem pass/docstring
            corpo = node.body

            # Remover docstrings
            if corpo and isinstance(corpo[0], ast.Expr) and isinstance(corpo[0].value, ast.Constant):
                corpo = corpo[1:]

            if not corpo:
                metodos_vazios.append(node.name)
            elif len(corpo) == 1 and isinstance(corpo[0], ast.Pass):
                # Se tem apenas pass, mas tem docstring, não é considerado vazio
                if not (node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant)):
                    metodos_vazios.append(node.name)
            elif len(corpo) == 1 and isinstance(corpo[0], ast.Expr):
                # Possível método com apenas um comentário
                metodos_incompletos.append(node.name)

    # Procurar por padrões problemáticos no código
    linhas = conteudo.split('\n')
    problemas = []
    imports_problematicos = []

    for i, linha in enumerate(linhas, 1):
        linha_stripped = linha.strip()

        # Verificar linhas que podem indicar métodos incompletos
        if linha_stripped.endswith(':') and not linha_stripped.startswith('#'):
            proxima_linha = linhas[i] if i < len(linhas) else ""
            if not proxima_linha.strip():
                problemas.append(f"Linha {i}: Possível método/bloco incompleto: {linha_stripped}")

        # Verificar TODO/FIXME/XXX
        if any(palavra in linha_stripped.upper() for palavra in ['TODO', 'FIXME', 'XXX', 'HACK']):
            problemas.append(f"Linha {i}: Marcador de pendência: {linha_stripped}")

        # Verificar imports problemáticos
        if linha_stripped.startswith('import ') or linha_stripped.startswith('from '):
            if 'import *' in linha_stripped:
                imports_problematicos.append(f"Linha {i}: Import * detectado: {linha_stripped}")

    # Retornar dados da análise
    return {
        'arquivo': nome_arquivo,
        'caminho': caminho_arquivo,
        'sintaxe_valida': True,
        'metodos_vazios': metodos_vazios,
        'metodos_incompletos': metodos_incompletos,
        'classes': classes,
        'problemas': problemas,
        'imports_problematicos': imports_problematicos,
        'linhas_totais': len(linhas),
        'linhas_nao_vazias': len([l for l in linhas if l.strip()]),
        'metodos_total': len([n for n in ast.walk(arvore) if isinstance(n, ast.FunctionDef)]),
        'classes_total': len(classes)
    }

def analisar_projeto():
    """Analisar todo o projeto Python"""
    print("🚀 ANÁLISE COMPLETA DO PROJETO BRAWL STARS CLONE")
    print("=" * 60)

    # Encontrar todos os arquivos Python
    arquivos_python = []

    # Arquivos principais
    if os.path.exists("main.py"):
        arquivos_python.append("main.py")

    # Arquivos na pasta src/
    if os.path.exists("src/"):
        arquivos_src = glob.glob("src/*.py")
        arquivos_python.extend(arquivos_src)

    # Arquivos de teste
    if os.path.exists("testes/"):
        arquivos_teste = glob.glob("testes/*.py")
        arquivos_python.extend(arquivos_teste)

    if not arquivos_python:
        print("❌ Nenhum arquivo Python encontrado!")
        return

    print(f"📁 Encontrados {len(arquivos_python)} arquivos Python:")
    for caminho in arquivos_python:
        print(f"   - {caminho}")

    # Analisar cada arquivo
    resultados = []
    problemas_graves = []

    for caminho_arquivo in arquivos_python:
        resultado_arquivo = analisar_arquivo(caminho_arquivo)
        if resultado_arquivo:
            resultados.append(resultado_arquivo)

            # Identificar problemas graves
            if resultado_arquivo['metodos_vazios']:
                problemas_graves.append(f"{resultado_arquivo['arquivo']}: {len(resultado_arquivo['metodos_vazios'])} métodos vazios")
            if resultado_arquivo['metodos_incompletos']:
                problemas_graves.append(f"{resultado_arquivo['arquivo']}: {len(resultado_arquivo['metodos_incompletos'])} métodos incompletos")
            if resultado_arquivo['imports_problematicos']:
                problemas_graves.append(f"{resultado_arquivo['arquivo']}: {len(resultado_arquivo['imports_problematicos'])} imports problemáticos")
        else:
            problemas_graves.append(f"{caminho_arquivo}: Falha na análise")

    # Relatório geral
    print("\n📊 RELATÓRIO GERAL DO PROJETO")
    print("=" * 40)

    if problemas_graves:
        print(f"🚨 PROBLEMAS GRAVES DETECTADOS ({len(problemas_graves)}):")
        for problema_grave in problemas_graves:
            print(f"   - {problema_grave}")
    else:
        print("✅ Nenhum problema grave detectado!")

    # Estatísticas gerais
    total_linhas = sum(r['linhas_totais'] for r in resultados)
    total_metodos = sum(r['metodos_total'] for r in resultados)
    total_classes = sum(r['classes_total'] for r in resultados)
    total_problemas = sum(len(r['problemas']) for r in resultados)

    print("\n📈 ESTATÍSTICAS GERAIS")
    print("-" * 25)
    print(f"Arquivos analisados: {len(resultados)}")
    print(f"Linhas totais: {total_linhas}")
    print(f"Métodos totais: {total_metodos}")
    print(f"Classes totais: {total_classes}")
    print(f"Problemas detectados: {total_problemas}")

    return resultados

def analisar_arquivo_game():
    """Manter compatibilidade com versão anterior"""
    return analisar_arquivo("src/game.py")

if __name__ == "__main__":
    # Se argument for passado, analisar arquivo específico
    if len(sys.argv) > 1:
        if sys.argv[1] == "--projeto" or sys.argv[1] == "-p":
            analisar_projeto()
        else:
            arquivo = sys.argv[1]
            resultado = analisar_arquivo(arquivo)
            if resultado:
                # Imprimir relatório detalhado para arquivo específico
                print("\n📊 RELATÓRIO DE ANÁLISE")
                print("-" * 30)

                if resultado['metodos_vazios']:
                    print(f"⚠️  Métodos vazios encontrados ({len(resultado['metodos_vazios'])}):")
                    for metodo in resultado['metodos_vazios']:
                        print(f"   - {metodo}")
                else:
                    print("✅ Nenhum método vazio encontrado")

                if resultado['metodos_incompletos']:
                    print(f"\n⚠️  Métodos possivelmente incompletos ({len(resultado['metodos_incompletos'])}):")
                    for metodo in resultado['metodos_incompletos']:
                        print(f"   - {metodo}")
                else:
                    print("✅ Nenhum método incompleto detectado")

                if resultado['problemas']:
                    print(f"\n⚠️  Possíveis problemas encontrados ({len(resultado['problemas'])}):")
                    for problema in resultado['problemas']:
                        print(f"   - {problema}")
                else:
                    print("✅ Nenhum problema óbvio detectado")

                if resultado['imports_problematicos']:
                    print(f"\n🚨 Imports problemáticos ({len(resultado['imports_problematicos'])}):")
                    for imp in resultado['imports_problematicos']:
                        print(f"   - {imp}")

                print("\n📈 ESTATÍSTICAS")
                print("-" * 20)
                print(f"Linhas totais: {resultado['linhas_totais']}")
                print(f"Linhas não vazias: {resultado['linhas_nao_vazias']}")
                print(f"Métodos definidos: {resultado['metodos_total']}")
                print(f"Classes definidas: {resultado['classes_total']}")
    else:
        # Por padrão, analisar todo o projeto
        analisar_projeto()
