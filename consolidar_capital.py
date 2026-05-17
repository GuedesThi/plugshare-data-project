import pandas as pd
import os

def consolidar_capital():
    arquivos_alvo = [
        "BASE_CAPITAL_CENTRO_ZS.xlsx",
        "BASE_CAPITAL_BARRA.xlsx",
        "BASE_CAPITAL_TIJUCA_ZN.xlsx",
        "BASE_CAPITAL_RECREIO.xlsx"
    ]
    
    lista_dfs = []
    print("--- Iniciando Consolidação da Capital ---")
    
    for arquivo in arquivos_alvo:
        if os.path.exists(arquivo):
            df = pd.read_excel(arquivo)
            print(f"[OK] Lendo {arquivo}: {len(df)} postos.")
            lista_dfs.append(df)

    if not lista_dfs:
        print("[ERRO] Nenhum arquivo da capital encontrado.")
        return

    df_final = pd.concat(lista_dfs, ignore_index=True)
    
    # Remove duplicatas pelo ID
    df_final = df_final.drop_duplicates(subset=['ID'])
    
    # Define a ordem final das colunas
    ordem_colunas = [
        "ID", "Código", "Município", "Nome", "Endereço", "Bairro", 
        "Tipo de Carregamento do Eletroposto", "Qde.", "Acesso", 
        "Latitude", "Longitude"
    ]
    
    df_final = df_final.reindex(columns=ordem_colunas)
    
    df_final.to_excel("BASE_CAPITAL_COMPLETA_FINAL.xlsx", index=False)
    print(f"Sucesso! Gerado: BASE_CAPITAL_COMPLETA_FINAL.xlsx")

if __name__ == "__main__":
    consolidar_capital()