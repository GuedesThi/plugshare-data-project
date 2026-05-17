import subprocess
import time
import sys
import os

# Importamos a função de consolidação
try:
    from consolidar_baixada import consolidar_baixada
except ImportError:
    print("[ERRO] Arquivo consolidar_baixada.py não encontrado!")

scripts = ["scan_baixada.py"]

def iniciar_maratona():
    print(f"--- Iniciando Maratona de Coleta ---")
    python_exec = sys.executable 

    for script in scripts:
        print(f"\n" + "="*50)
        print(f"AGORA INICIANDO: {script}")
        print("="*50)
        processo = subprocess.run([python_exec, script])
        
        if processo.returncode == 0:
            print(f"\n[OK] {script} finalizado com sucesso!")
        else:
            print(f"\n[ERRO] {script} falhou.")
            return 
        
        time.sleep(10)

    print(f"\n" + "="*50)
    print("INICIANDO CONSOLIDAÇÃO DOS DADOS")
    print("="*50)
    consolidar_baixada()

if __name__ == "__main__":
    iniciar_maratona()