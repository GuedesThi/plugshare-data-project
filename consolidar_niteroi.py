import pandas as pd
import os
import glob

def consolidar_niteroi():
    # Busca dinâmica para evitar erros de nome de arquivo
    arquivos_encontrados = glob.glob("BASE_NITEROI_*.xlsx")
    
    lista_dfs = []
    print("\n--- Iniciando Consolidação de Niterói ---")
    
    for arquivo in arquivos_encontrados:
        if "COMPLETA_FINAL" in arquivo: continue
        try:
            df = pd.read_excel(arquivo)
            print(f"[OK] Lendo {arquivo}: {len(df)} postos encontrados.")
            lista_dfs.append(df)
        except Exception as e:
            print(f"[ERRO] Falha ao ler {arquivo}: {e}")

    if not lista_dfs:
        print("[ERRO] Nenhum arquivo de Niterói encontrado para consolidar.")
        return

    df_final = pd.concat(lista_dfs, ignore_index=True)
    df_final = df_final.drop_duplicates(subset=['ID'])
    
    ordem_colunas = [
        "ID", "Código", "Município", "Nome", "Endereço", "Bairro", 
        "Tipo de Carregamento do Eletroposto", "Qde.", "Acesso", 
        "Latitude", "Longitude"
    ]
    
    df_final = df_final.reindex(columns=ordem_colunas)
    
    nome_saida = "BASE_NITEROI_COMPLETA_FINAL.xlsx"
    df_final.to_excel(nome_saida, index=False)
    print(f"\nSUCESSO! Gerado: {nome_saida}")

if __name__ == "__main__":
    consolidar_niteroi()