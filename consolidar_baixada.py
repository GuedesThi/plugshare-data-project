import pandas as pd
import os

def consolidar_baixada():
    arquivos_alvo = [
        "BASE_BAIXADA_NI_QUEIMADOS.xlsx",
        "BASE_BAIXADA_CAXIAS_PROF.xlsx",
        "BASE_BAIXADA_MERITI_NILOPOLIS.xlsx",
        "BASE_BAIXADA_SEROPEDICA_ROAD.xlsx"
    ]
    
    lista_dfs = []
    print("--- Iniciando Consolidação Final ---")
    
    for arquivo in arquivos_alvo:
        if os.path.exists(arquivo):
            df = pd.read_excel(arquivo)
            print(f"[OK] Lendo {arquivo}: {len(df)} postos.")
            lista_dfs.append(df)

    if not lista_dfs:
        print("[ERRO] Nada para consolidar.")
        return

    df_final = pd.concat(lista_dfs, ignore_index=True)
    
    # Remove duplicatas baseadas no ID capturado
    df_final = df_final.drop_duplicates(subset=['ID'])
    
    # Reordena as colunas conforme o seu pedido
    ordem_colunas = [
        "ID", "Código", "Município", "Nome", "Endereço", "Bairro", 
        "Tipo de Carregamento do Eletroposto", "Qde.", "Acesso", 
        "Latitude", "Longitude"
    ]
    
    # Filtra apenas colunas existentes para evitar erro
    df_final = df_final.reindex(columns=ordem_colunas)
    
    df_final.to_excel("BASE_BAIXADA_COMPLETA_FINAL.xlsx", index=False)
    print(f"Sucesso! Gerado: BASE_BAIXADA_COMPLETA_FINAL.xlsx")

if __name__ == "__main__":
    consolidar_baixada()