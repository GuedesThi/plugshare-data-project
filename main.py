import time, json, os, gc, math, pandas as pd
from playwright.sync_api import sync_playwright

def calcular_distancia_entre_postos(lat1, lon1, lat2, lon2):
    R = 6371000 
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))

def executar_sessao(lat, lon, ids_vistos, zoom, region_name, bounds, max_tentativas=3):
    tentativa = 1
    while tentativa <= max_tentativas:
        estacoes_no_quadrante = []
        with sync_playwright() as p:
            browser = p.firefox.launch(headless=False)
            context = browser.new_context(
                viewport={'width': 960, 'height': 1000}, 
                permissions=['geolocation'],
                geolocation={'latitude': lat, 'longitude': lon}
            )
            page = context.new_page()
            try: page.evaluate("() => { window.moveTo(0,0); window.resizeTo(960, 1000); }")
            except: pass

            def handle_response(response):
                if "locations" in response.url and response.status == 200:
                    try:
                        data = response.json()
                        stations = []
                        if isinstance(data, list): stations = data
                        elif isinstance(data, dict): stations = data.get('locations', [])
                        
                        for s in stations:
                            s_id = s.get('id')
                            if not s_id: continue 
                            s_lat, s_lon = s.get('latitude'), s.get('longitude')
                            
                            # Geofencing com margem mínima (0.01) para precisão
                            if not (bounds['lat_s'] - 0.01 <= s_lat <= bounds['lat_n'] + 0.01 and 
                                    bounds['lon_o'] - 0.01 <= s_lon <= bounds['lon_l'] + 0.01):
                                continue

                            if s_id and s_id not in ids_vistos:
                                estacoes_no_quadrante.append(s)
                                ids_vistos.add(s_id)
                                print(f"      [CAPTURA] {s.get('name')} | ID: {s_id}")
                    except: pass

            page.on("response", handle_response)
            
            try:
                url = f"https://www.plugshare.com/?lat={lat}&lng={lon}&z={zoom}"
                page.goto(url, wait_until="commit", timeout=45000)
                
                # --- SISTEMA DE MODAL COM RETRY FORÇADO ---
                btn_cancel = page.get_by_role("button", name="cancel")
                try:
                    btn_cancel.wait_for(state="visible", timeout=10000)
                    btn_cancel.click()
                    page.wait_for_timeout(2000)
                except:
                    page.keyboard.press("Escape")
                    page.wait_for_timeout(2000)

                # Se o modal ainda estiver lá, EXPLODE um erro para forçar a T2, T3...
                if btn_cancel.is_visible():
                    print(f"      [FALHA] Modal persistente na T{tentativa}. Reiniciando...")
                    raise RuntimeError("Interface bloqueada pelo modal")

                # Provocação de Mapa (Scroll)
                for _ in range(2):
                    page.mouse.wheel(0, 300)
                    page.wait_for_timeout(1000)
                    page.mouse.wheel(0, -300)
                    page.wait_for_timeout(1000)

                page.wait_for_timeout(5000)
                browser.close()
                return estacoes_no_quadrante

            except Exception as e:
                print(f"      [RETRY] Tentativa {tentativa} falhou: {e}")
                browser.close()
                tentativa += 1
                time.sleep(2)
                gc.collect()
    return []

def rodar_scrapper_regional(lat_n, lat_s, lon_o, lon_l, div_lat, div_lon, zoom, name):
    bounds = {'lat_n': lat_n, 'lat_s': lat_s, 'lon_o': lon_o, 'lon_l': lon_l}
    checkpoint_file = f"checkpoint_{name}.json"
    ids_vistos = set()
    ultimo_idx = -1
    
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, "r") as f:
            data = json.load(f)
            ids_vistos = set(data.get("ids", []))
            ultimo_idx = data.get("ultimo_indice", -1)

    lats = [lat_n + (lat_s - lat_n) * i / (div_lat - 1) for i in range(div_lat)] if div_lat > 1 else [lat_n]
    lons = [lon_o + (lon_l - lon_o) * i / (div_lon - 1) for i in range(div_lon)] if div_lon > 1 else [lon_o]
    grade = [(round(la, 6), round(lo, 6)) for la in lats for lo in lons]
    
    acumulado = []
    print(f"\nIniciando {name.upper()} | {len(grade)} pontos.")

    try:
        for i, (lat, lon) in enumerate(grade):
            if i <= ultimo_idx: continue
            print(f">>> {name} {i+1}/{len(grade)} | Total: {len(ids_vistos)}")
            novos = executar_sessao(lat, lon, ids_vistos, zoom, name, bounds)
            acumulado.extend(novos)
            with open(checkpoint_file, "w") as f:
                json.dump({"ids": list(ids_vistos), "ultimo_indice": i}, f)
    finally:
        if acumulado:
            df = pd.DataFrame([{
                "ID": s.get('id'), "Nome": str(s.get('name')).upper(),
                "Endereco": str(s.get('address', '')).replace('\n', ' ').upper(),
                "Latitude": s.get('latitude'), "Longitude": s.get('longitude')
            } for s in acumulado])
            df.to_excel(f"BASE_{name.upper()}.xlsx", index=False)