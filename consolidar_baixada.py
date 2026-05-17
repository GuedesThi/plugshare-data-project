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
    print("--- Iniciando Consolidação ---")
    
    for arquivo in arquivos_alvo:
        if os.path.exists(arquivo):
            df = pd.read_excel(arquivo)
            print(f"[OK] Lendo {arquivo}: {len(df)} postos.")
            lista_dfs.append(df)

    if not lista_dfs:
        print("[ERRO] Nada para consolidar.")
        return

    df_final = pd.concat(lista_dfs, ignore_index=True)
    df_final = df_final.drop_duplicates(subset=['ID'])
    
    df_final.to_excel("BASE_BAIXADA_COMPLETA.xlsx", index=False)
    print(f"Sucesso! Arquivo gerado: BASE_BAIXADA_COMPLETA.xlsx")

if __name__ == "__main__":
    consolidar_baixada()