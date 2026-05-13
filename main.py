import time
import math
import json
import os
import gc
import pandas as pd
from playwright.sync_api import sync_playwright

# --- CONFIGURAÇÃO CAPITAL RJ ---
LAT_NORTE, LAT_SUL = -22.85, -23.05
LON_OESTE, LON_LESTE = -43.55, -43.15
DIVISOES_LAT, DIVISOES_LON = 8, 12
ZOOM_LEVEL = 15
CHECKPOINT_FILE = "checkpoint_capital_rj.json"

CONNECTOR_TYPES = {
    1: "J-1772", 2: "Tesla", 3: "NEMA 5-15", 4: "CHAdeMO",
    5: "CCS1", 6: "Tipo 2", 7: "Tipo 2", 13: "Wallbox",
    20: "CCS2", 49: "Tipo 2"
}

def decimal_para_dms(lat, lon):
    def converter(valor, pos, neg):
        direcao = pos if valor >= 0 else neg
        valor = abs(valor)
        graus = int(valor)
        minutos = int((valor - graus) * 60)
        segundos = ((valor - graus) * 60 - minutos) * 60
        return f'{graus}º{minutos}\'{segundos:.2f}"{direcao}'
    return converter(lat, 'N', 'S'), converter(lon, 'E', 'W')

def carregar_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        try:
            with open(CHECKPOINT_FILE, "r") as f:
                data = json.load(f)
                return set(data.get("ids", [])), data.get("ultimo_indice", -1)
        except: pass
    return set(), -1

def salvar_checkpoint(ids_vistos, indice_atual):
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump({"ids": list(ids_vistos), "ultimo_indice": indice_atual}, f)

def executar_sessao(lat, lon, ids_vistos, max_tentativas=3):
    tentativa = 1
    
    while tentativa <= max_tentativas:
        estacoes_no_quadrante = []
        with sync_playwright() as p:
            browser = p.firefox.launch(headless=True)
            context = browser.new_context(
                viewport={'width': 1280, 'height': 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0",
                permissions=['geolocation'],
                geolocation={'latitude': lat, 'longitude': lon}
            )
            page = context.new_page()
            page.route("**/*.{png,jpg,jpeg,svg,woff2}", lambda r: r.abort())

            def handle_response(response):
                if "locations" in response.url and response.status == 200:
                    try:
                        data = response.json()
                        stations = data if isinstance(data, list) else []
                        for s in stations:
                            s_id = s.get('id')
                            if s_id and s_id not in ids_vistos:
                                addr = str(s.get('address', '')).upper()
                                if " RIO DE JANEIRO" in addr or ", RJ" in addr:
                                    estacoes_no_quadrante.append(s)
                                    ids_vistos.add(s_id)
                    except: pass

            page.on("response", handle_response)

            try:
                url = f"https://www.plugshare.com/?lat={lat}&lng={lon}&z={ZOOM_LEVEL}"
                page.goto(url, wait_until="commit", timeout=45000)

                # --- FECHAMENTO OBRIGATÓRIO DO MODAL ---
                try:
                    btn = page.get_by_role("button", name="cancel")
                    btn.wait_for(state="visible", timeout=12000) # Espera ser visível
                    page.evaluate("el => el.click()", btn.element_handle())
                    print(f"      [OK] Modal fechado na T{tentativa}.")
                except Exception:
                    # Se falhar o botão, tentamos Escape
                    page.keyboard.press("Escape")
                    page.wait_for_timeout(2000)
                    
                    # Verificação Final: O modal ainda está lá?
                    if page.get_by_role("button", name="cancel").is_visible():
                        print(f"      [ERRO] Modal persistente na T{tentativa}!")
                        raise RuntimeError("Modal não fechou") # Força a ida para o 'except' externo
                    else:
                        print(f"      [OK] Modal fechado via Escape na T{tentativa}.")

                # --- GATILHO E COLETA ---
                page.mouse.wheel(0, 100)
                page.wait_for_timeout(1000)
                page.mouse.wheel(0, -100)

                start_wait = time.time()
                while time.time() - start_wait < 10:
                    if len(estacoes_no_quadrante) > 0: break
                    page.wait_for_timeout(500)
                
                print(f"      [RESULTADO] {len(estacoes_no_quadrante)} novos postos.")
                browser.close()
                return estacoes_no_quadrante # Sai do 'while' de tentativas com sucesso

            except Exception as e:
                print(f"      [RETRY] Tentativa {tentativa} falhou: {e}. Reiniciando...")
                browser.close()
                tentativa += 1
                time.sleep(3)
                gc.collect()

    return [] # Retorna vazio só se esgotar as 3 tentativas

def processar_base(estacoes):
    if not estacoes: return pd.DataFrame()
    processados = []
    for s in estacoes:
        lat, lon = s.get('latitude'), s.get('longitude')
        lat_dms, lon_dms = decimal_para_dms(lat, lon)
        conns = {CONNECTOR_TYPES.get(o.get('connector'), "Outro") 
                 for st in s.get('stations', []) for o in st.get('outlets', [])}
        processados.append({
            "ID": s.get('id'), "Nome": str(s.get('name')).upper(), "Score": s.get('score', 0),
            "Endereco": str(s.get('address', '')).replace('\n', ' ').upper(),
            "Conectores": ", ".join(conns), "Lat_DMS": lat_dms, "Lon_DMS": lon_dms,
            "Latitude": lat, "Longitude": lon
        })
    return pd.DataFrame(processados)

def main():
    lats = [LAT_NORTE + (LAT_SUL - LAT_NORTE) * i / (DIVISOES_LAT - 1) for i in range(DIVISOES_LAT)]
    lons = [LON_OESTE + (LON_LESTE - LON_OESTE) * i / (DIVISOES_LON - 1) for i in range(DIVISOES_LON)]
    grade = [(round(lat, 6), round(lon, 6)) for lat in lats for lon in lons]
    
    ids_vistos, ultimo_idx = carregar_checkpoint()
    acumulado_total = []

    print(f"Iniciando Varredura CAPITAL RJ: {len(grade)} pontos.")

    try:
        for i, (lat, lon) in enumerate(grade):
            if i <= ultimo_idx: continue
            
            print(f">>> Quadrante {i+1}/{len(grade)} | Total Únicos: {len(ids_vistos)}")
            novos = executar_sessao(lat, lon, ids_vistos)
            acumulado_total.extend(novos)
            salvar_checkpoint(ids_vistos, i)
            
            if (i + 1) % 15 == 0:
                processar_base(acumulado_total).to_excel(f"backup_capital_{i+1}.xlsx", index=False)
                
    except KeyboardInterrupt:
        print("\nInterrompido.")
    finally:
        df = processar_base(acumulado_total)
        if not df.empty:
            df.to_excel("BASE_CAPITAL_RJ_FINAL.xlsx", index=False)
            print(f"Finalizado. {len(df)} postos da Capital salvos.")

if __name__ == "__main__":
    main()