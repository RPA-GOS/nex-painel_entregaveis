"""
Script de debug para investigar por que 'nti' não aparece na primeira página
"""
import pandas as pd
from controllers.main_controller import MainController
from utils.constants import AREAS_MAP

controller = MainController()

print("=" * 80)
print("DEBUG: Investigando dados do 'nti'")
print("=" * 80)

# Carregar dados
df_rpa = controller.load_data()
print(f"\n1. Total de registros carregados: {len(df_rpa)}")

# Verificar se existe coluna nome_processo
if 'nome_processo' in df_rpa.columns:
    # Filtrar registros que começam com 'nti'
    nti_registros = df_rpa[df_rpa['nome_processo'].str.lower().str.startswith('nti', na=False)]
    print(f"\n2. Registros com nome_processo começando com 'nti': {len(nti_registros)}")

    if len(nti_registros) > 0:
        print("\n3. Exemplos de processos 'nti' encontrados:")
        print(nti_registros[['nome_processo', 'sigla', 'area_nome']].head(3))

        # Verificar a sigla extraída
        if 'sigla' in nti_registros.columns:
            siglas_unicas = nti_registros['sigla'].unique()
            print(f"\n4. Siglas únicas extraídas dos processos 'nti': {siglas_unicas}")

        # Verificar area_nome
        if 'area_nome' in nti_registros.columns:
            areas_unicas = nti_registros['area_nome'].unique()
            print(f"\n5. Áreas únicas atribuídas aos processos 'nti': {areas_unicas}")
    else:
        print("\n⚠️ PROBLEMA: Nenhum registro com 'nti' foi encontrado no nome_processo!")
        print("\nVerificando os primeiros processos carregados:")
        print(df_rpa[['nome_processo', 'sigla', 'area_nome']].head(10))

# Verificar contagem por área
contagem_por_area = controller.get_area_counts(df_rpa)
print(f"\n6. Contagem por área:")
for area, count in sorted(contagem_por_area.items()):
    print(f"   - {area}: {count}")

# Verificar se 'Núcleo de TI' está na contagem
if 'Núcleo de TI' in contagem_por_area:
    print(f"\n✓ 'Núcleo de TI' ENCONTRADO com {contagem_por_area['Núcleo de TI']} execuções")
else:
    print("\n✗ 'Núcleo de TI' NÃO ENCONTRADO na contagem")

# Verificar AREAS_MAP
print(f"\n7. AREAS_MAP contém 'nti': {'nti' in AREAS_MAP}")
if 'nti' in AREAS_MAP:
    print(f"   Valor: {AREAS_MAP['nti']}")

print("\n" + "=" * 80)