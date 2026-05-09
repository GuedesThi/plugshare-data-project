from playwright.sync_api import sync_playwright
import math
import time
import pandas as pd

CONNECTOR_TYPES = {
    1: "J-1772", 2: "Tesla", 3: "NEMA 5-15", 4: "CHAdeMO",
    5: "CCS1", 6: "Tipo 2", 7: "Tipo 2", 13: "Wallbox",
    20: "CCS2", 49: "Tipo 2"
}

RJ_BOUNDS = {
    "lat_min": -23.08, "lat_max": -22.74,
    "lon_min": -43.79, "lon_max": -43.10
}

COORDENADAS_ALVO = [
    {"lat": -22.9068, "lon": -43.1729}, # 1. Centro / Porto Maravilha
    {"lat": -22.9519, "lon": -43.1850}, # 2. Botafogo / Flamengo
    {"lat": -22.9644, "lon": -43.2185}, # 3. Lagoa / Jardim Botânico
    {"lat": -22.9839, "lon": -43.2173}, # 4. Leblon / Ipanema
    {"lat": -22.8953, "lon": -43.2241}, # 5. São Cristóvão / Benfica
    {"lat": -22.9250, "lon": -43.2350}, # 6. Tijuca / Maracanã
    {"lat": -22.8916, "lon": -43.2800}, # 7. Méier / Cachambi
    {"lat": -23.0003, "lon": -43.3659}, # 8. Barra da Tijuca (Início/Jardim Oceânico)
    {"lat": -22.9841, "lon": -43.4150}, # 9. Barra da Tijuca (Via Parque/Alvorada)
    {"lat": -23.0189, "lon": -43.4650}  # 10. Recreio dos Bandeirantes
]

ids_processados = set()
historico_postos = []
dados_finais = []

def coordenada_pertence_ao_rj(lat, lon):
    return (RJ_BOUNDS['lat_min'] <= lat <= RJ_BOUNDS['lat_max'] and
            RJ_BOUNDS['lon_min'] <= lon <= RJ_BOUNDS['lon_max'])

def decimal_to_dms(lat, lon):
    def convert(value, pos, neg):
        direction = pos if value >= 0 else neg
        value = abs(value)
        degrees = int(value)
        minutes_float = (value - degrees) * 60
        minutes = int(minutes_float)
        seconds = (minutes_float - minutes) * 60
        return f'{degrees}º{minutes}\'{seconds:.2f}"{direction}'
    return convert(lat, 'N', 'S'), convert(lon, 'E', 'W')

def calcular_distancia_entre_postos(lat1, lon1, lat2, lon2):
    R = 6371000 
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def verificar_proximidade_entre_postos(novo_id, novo_lat, novo_lon):
    conflitos = []
    limite_metros = 15.0
    for posto in historico_postos:
        if posto['id'] == novo_id: continue
        distancia = calcular_distancia_entre_postos(novo_lat, novo_lon, posto['lat'], posto['lon'])
        if distancia <= limite_metros:
            conflitos.append(f"ID {posto['id']} ({distancia:.2f}m)")
    return conflitos

def processar_estacao(s):
    try:
        s_id = s.get('id')
        lat_dec, lon_dec = s.get('latitude'), s.get('longitude')
        lat_dms, lon_dms = decimal_to_dms(lat_dec, lon_dec)
        
        conflitos = verificar_proximidade_entre_postos(s_id, lat_dec, lon_dec)
        obs_text = f"CONFLITO: {', '.join(conflitos)}" if conflitos else ""

        conectores_count = {}
        for st in s.get('stations', []):
            for out in st.get('outlets', []):
                c_id = out.get('connector')
                nome_c = CONNECTOR_TYPES.get(c_id, f"Tipo {c_id}")
                conectores_count[nome_c] = conectores_count.get(nome_c, 0) + 1

        for tipo, qde in conectores_count.items():
            dados_finais.append({
                "Código": "",      
                "Município": "",   
                "Bairro": "",      
                "ID": s_id,
                "Nome": s.get('name'),
                "Endereço": s.get('address', 'N/A'),
                "Latitude": lat_dms,
                "Longitude": lon_dms,
                "Acesso": "Público" if s.get('access') == 1 else "Restrito",
                "Tipo de Carregamento": tipo,
                "Qde.": qde,
                "Score": s.get('score', 0.0),
                "OBS": obs_text
            })
        
        historico_postos.append({'id': s_id, 'lat': lat_dec, 'lon': lon_dec, 'nome': s.get('name')})
        ids_processados.add(s_id)
    except Exception as e:
        print(f"Erro ao processar posto {s.get('id')}: {e}")

def executar_sessao(idx, lat, lon):
    tentativa = 1
    while True:
        print(f">>> Sessão {idx+1}/10 | Pos: {lat}, {lon} | Tentativa: {tentativa}")
        with sync_playwright() as p:
            browser = p.firefox.launch(headless=True)
            context = browser.new_context(
                permissions=['geolocation'], 
                geolocation={'latitude': lat, 'longitude': lon},
                viewport={'width': 1280, 'height': 720}
            )
            page = context.new_page()
            
            # Bloqueia mídias para acelerar as 10 sessões
            page.route("**/*.{png,jpg,jpeg,svg,css,woff2}", lambda r: r.abort())

            def handle_response(response):
                if "locations" in response.url and response.status == 200:
                    try:
                        stations = response.json()
                        if not isinstance(stations, list): return
                        for s in stations:
                            s_id = s.get('id')
                            if s_id in ids_processados: continue
                            
                            s_lat, s_lon = s.get('latitude'), s.get('longitude')
                            addr = str(s.get('address', '')).upper()
                            
                            if s.get('access') in [1, 2]:
                                if (" RJ" in addr or "RIO DE JANEIRO" in addr) or coordenada_pertence_ao_rj(s_lat, s_lon):
                                    processar_estacao(s)
                    except: pass

            page.on("response", handle_response)
            try:
                page.goto("https://www.plugshare.com/", wait_until="domcontentloaded", timeout=60000)
                btn_cancel = page.get_by_role("button", name="cancel")
                btn_cancel.wait_for(state="visible", timeout=20000)
                btn_cancel.click()
                
                page.wait_for_timeout(15000) 
                browser.close()
                break 
            except Exception as e:
                print(f"Falha na tentativa {tentativa}: Reiniciando sessão...")
                browser.close()
                tentativa += 1
                time.sleep(5)

def exportar_dados():
    if not dados_finais:
        print("Nenhum dado coletado.")
        return
    
    df = pd.DataFrame(dados_finais)
    colunas = ["Código", "Município", "Bairro", "ID", "Nome", "Endereço", "Latitude", "Longitude", "Acesso", "Tipo de Carregamento", "Qde.", "Score", "OBS"]
    df = df[colunas]
    
    filename = f"relatorio_eletropostos_rj_10_coordenadas.xlsx"
    df.to_excel(filename, index=False, engine='openpyxl')
    print(f"\nSucesso! Planilha gerada: {filename}")
    print(f"Total de registros únicos coletados: {len(df)}")

if __name__ == "__main__":
    start_total = time.time()
    for idx, coord in enumerate(COORDENADAS_ALVO):
        executar_sessao(idx, coord['lat'], coord['lon'])
    exportar_dados()
    print(f"Tempo total: {time.time() - start_total:.2f}s")