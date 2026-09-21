"""
Debug: Verificar ordem e areas exibidas na tela inicial
"""
from controllers.main_controller import MainController
from utils.constants import AREAS_MAP

controller = MainController()

print("=" * 80)
print("DEBUG: Ordem de exibicao das areas na tela inicial")
print("=" * 80)

df_rpa = controller.load_data()
contagem_por_area = controller.get_area_counts(df_rpa)

print(f"\nTotal de registros: {len(df_rpa)}")

# Replicar a lógica exata do main.py
areas_com_dados = {
    sigla: nome_area
    for sigla, nome_area in AREAS_MAP.items()
    if contagem_por_area.get(nome_area, 0) > 0
}

print(f"\nTotal de areas com dados: {len(areas_com_dados)}")
print("\nAreas que DEVERIAM aparecer na tela inicial:")
print("-" * 80)

for idx, (sigla, nome_area) in enumerate(areas_com_dados.items(), 1):
    qtd_execucoes = contagem_por_area.get(nome_area, 0)
    coluna = (idx - 1) % 3 + 1
    linha = (idx - 1) // 3 + 1
    print(f"{idx}. [{sigla}] {nome_area}: {qtd_execucoes} execucoes (Linha {linha}, Coluna {coluna})")

print("\n" + "=" * 80)
print("\nVerificacao especifica do 'nti':")
print("-" * 80)
if 'nti' in areas_com_dados:
    print(f"OK - 'nti' esta em areas_com_dados")
    print(f"     Nome: {areas_com_dados['nti']}")
    print(f"     Contagem: {contagem_por_area.get(areas_com_dados['nti'], 0)}")
else:
    print("PROBLEMA - 'nti' NAO esta em areas_com_dados")
    print(f"'nti' in AREAS_MAP? {('nti' in AREAS_MAP)}")
    print(f"'Nucleo de TI' in contagem_por_area? {('Nucleo de TI' in contagem_por_area)}")
    if 'Nucleo de TI' in contagem_por_area:
        print(f"Contagem: {contagem_por_area['Nucleo de TI']}")

print("\n" + "=" * 80)