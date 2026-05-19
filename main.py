import time, json, os, gc, math, pandas as pd
from playwright.sync_api import sync_playwright

CONNECTOR_TYPES = {
    1: "J-1772", 2: "Tesla", 3: "NEMA 5-15", 4: "CHAdeMO", 
    5: "CCS1", 6: "Tipo 2", 7: "Tipo 2", 13: "Wallbox", 
    20: "CCS2", 49: "Tipo 2"
}

def decimal_to_dms(lat, lon):
    def convert(value, pos, neg):
        direction = pos if value >= 0 else neg
        value = abs(value)
        degrees = int(value)
        minutes_float = (value - degrees) * 60
        minutes = int(minutes_float)
        seconds = (minutes_float - minutes) * 60
        return f'{degrees}º{minutes}\'{seconds:.2f}"{direction}'
    lat_dms = convert(lat, 'N', 'S')
    lon_dms = convert(lon, 'E', 'W')
    return lat_dms, lon_dms

def executar_sessao(lat, lon, ids_vistos, zoom, region_name, max_tentativas=3):
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
                        stations = data if isinstance(data, list) else data.get('locations', [])
                        for s in stations:
                            s_id = s.get('id')
                            s_lat = s.get('latitude')
                            s_lon = s.get('longitude')
                            
                            # Filtro Geofencing RJ
                            if s_lat and s_lon:
                                if not (-24.0 < s_lat < -21.0 and -45.0 < s_lon < -40.0):
                                    continue

                            if s_id and s_id not in ids_vistos:
                                # Processamento de detalhes
                                lat_dms, lon_dms = decimal_to_dms(s_lat, s_lon)
                                acesso_desc = "Público" if s.get('access') == 1 else "Restrito"
                                
                                specs = []
                                qtde = 0
                                for st in s.get('stations', []):
                                    for out in st.get('outlets', []):
                                        qtde += 1
                                        conn_name = CONNECTOR_TYPES.get(out.get('connector'), "Tipo 2")
                                        specs.append(conn_name)
                                
                                tipo_carregamento = ", ".join(sorted(list(set(specs)))) if specs else "Tipo 2"

                                estacoes_no_quadrante.append({
                                    "ID": s_id,
                                    "Código": "",
                                    "Município": "",
                                    "Nome": str(s.get('name', '')).upper(),
                                    "Endereço": str(s.get('address', '')).replace('\n', ' ').upper(),
                                    "Bairro": "",
                                    "Tipo de Carregamento do Eletroposto": tipo_carregamento,
                                    "Qde.": qtde if qtde > 0 else 1,
                                    "Acesso": acesso_desc,
                                    "Latitude": lat_dms,
                                    "Longitude": lon_dms
                                })
                                ids_vistos.add(s_id)
                    except: pass

            page.on("response", handle_response)
            try:
                url = f"https://www.plugshare.com/?lat={lat}&lng={lon}&z={zoom}"
                page.goto(url, wait_until="commit", timeout=45000)
                try:
                    btn = page.get_by_role("button", name="cancel")
                    btn.wait_for(state="visible", timeout=12000)
                    page.evaluate("el => el.click()", btn.element_handle())
                except:
                    page.keyboard.press("Escape")
                    if page.get_by_role("button", name="cancel").is_visible():
                        raise RuntimeError("Modal persistente")

                page.mouse.wheel(0, 100)
                page.wait_for_timeout(1000)
                page.mouse.wheel(0, -100)

                start_wait = time.time()
                while time.time() - start_wait < 10:
                    if len(estacoes_no_quadrante) > 0: break
                    page.wait_for_timeout(500)
                
                browser.close()
                return estacoes_no_quadrante
            except Exception as e:
                print(f"      [RETRY] {region_name} T{tentativa} falhou.")
                browser.close()
                tentativa += 1
                time.sleep(3)
                gc.collect()
    return []

def rodar_scrapper_regional(lat_n, lat_s, lon_o, lon_l, div_lat, div_lon, zoom, name):
    checkpoint_file = f"checkpoint_{name}.json"
    ids_vistos = set()
    ultimo_idx = -1
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, "r") as f:
            data = json.load(f)
            ids_vistos, ultimo_idx = set(data.get("ids", [])), data.get("ultimo_indice", -1)

    lats = [lat_n + (lat_s - lat_n) * i / (div_lat - 1) for i in range(div_lat)]
    lons = [lon_o + (lon_l - lon_o) * i / (div_lon - 1) for i in range(div_lon)]
    grade = [(round(la, 6), round(lo, 6)) for la in lats for lo in lons]
    
    acumulado = []
    print(f"\nIniciando {name.upper()} | {len(grade)} pontos.")

    try:
        for i, (lat, lon) in enumerate(grade):
            if i <= ultimo_idx: continue
            print(f">>> {name} {i+1}/{len(grade)} | Total: {len(ids_vistos)}")
            novos = executar_sessao(lat, lon, ids_vistos, zoom, name)
            acumulado.extend(novos)
            with open(checkpoint_file, "w") as f:
                json.dump({"ids": list(ids_vistos), "ultimo_indice": i}, f)
    finally:
        if acumulado:
            df = pd.DataFrame(acumulado)
            df.to_excel(f"BASE_{name.upper()}.xlsx", index=False)
            print(f"Arquivo {name} gerado!")