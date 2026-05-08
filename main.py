from playwright.sync_api import sync_playwright
import math

CONNECTOR_TYPES = {
    1: "J-1772",
    2: "Tesla",
    3: "NEMA 5-15",
    4: "CHAdeMO",
    5: "CCS1",
    6: "Tipo 2",
    7: "Tipo 2",
    13: "Wallbox",
    20: "CCS2",
    49: "Tipo 2"
}

RJ_BOUNDS = {
    "lat_min": -23.08,
    "lat_max": -22.74,
    "lon_min": -43.79,
    "lon_max": -43.10
}

ids_processados = set()
historico_postos = []

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
    R = 6371000 # raio da terra em metros

    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi/2)**2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c

def verificar_proximidade_entre_postos(novo_id, novo_lat, novo_lon):
    conflitos = []
    limite_metros = 15.0

    for posto in historico_postos:
        if posto['id'] == novo_id:
            continue

        distancia = calcular_distancia_entre_postos(novo_lat, novo_lon, posto['lat'], posto['lon'])

        if distancia <= limite_metros:
            conflitos.append({
                'id': posto['id'],
                'distancia': distancia,
                'nome': posto['nome']
            })

    return conflitos

def print_station_details(s, conflitos):
            name = s.get('name', 'N/A')
            s_id = s.get('id', 'N/A')
            addr = s.get('address', 'Sem endereço')
            score = s.get('score', 0.0)

            lat_dec = s.get('latitude')
            lon_dec = s.get('longitude')
            lat_dms, lon_dms = decimal_to_dms(lat_dec, lon_dec)

            access_desc = "Público" if s.get('access') == 1 else "Restrito"

            specs = []
            for st in s.get('stations', []):
                for out in st.get('outlets', []):
                    conn_id = out.get('connector')
                    if not conn_id:
                        continue
                    
                    conn_name = CONNECTOR_TYPES.get(conn_id, f"Desconhecido ({conn_id})")

                    pwr = out.get('kilowatts') or out.get('power') or out.get('amps')
                    pwr_label = f"{float(pwr):.1f}kW" if pwr else "s/i"

                    specs.append(f"{conn_name} | Potência: {pwr_label}")

            unique_specs = sorted(list(set(specs)))

            print(f"\n[Eletroposto Detectado]")
            print(f"ID: {s_id} | Nome: {name} | Score: {score}")
            print(f"Endereço: {addr}")
            print(f"Latitude: {lat_dms}")
            print(f"Longitude: {lon_dms}")
            print(f"Acesso: {access_desc} | Tipo: {', '.join(unique_specs)}")

            if conflitos:
                print(f'ALERTA DE PROXIMIDADE DETECTADO:')
                for c in conflitos:
                    print(f" - Conflito com ID {c['id']} ({c['nome']}) a {c['distancia']:.2f}m")

            print("-" * 60)

def run():
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=False)

        context = browser.new_context(
            permissions=['geolocation'], 
            viewport={'width': 1280, 'height': 720}, 
            geolocation={'latitude': -22.9068, 'longitude': -43.1729}
        )
        
        page = context.new_page()
        page.set_default_timeout(60000) # 60 segundos

        

        def handle_response(response):
            if "locations" in response.url and response.status == 200:
                try:
                    data = response.json()
                    stations = data if isinstance(data, list) else []

                    for station in stations:
                        s_id = station.get('id')
                        s_name = station.get('name')
                        lat = station.get('latitude')
                        lon = station.get('longitude')

                        if s_id in ids_processados: continue

                        address = str(station.get('address', '')).upper()
                        city = str(station.get('city', '')).upper()

                        if station.get('access') in [1, 2]:
                            pertence_ao_rj_str = any(key in address or key in city for key in ["RIO DE JANEIRO", " RJ"])

                            if pertence_ao_rj_str or coordenada_pertence_ao_rj(lat, lon):
                                conflitos = verificar_proximidade_entre_postos(s_id, lat, lon)
                                print_station_details(station, conflitos)
                                historico_postos.append({'id': s_id, 'lat': lat, 'lon': lon, 'nome': s_name})
                                ids_processados.add(s_id)
                                
                except Exception as error:
                    print(f"Houve um erro na coleta dos dados {error}")

        page.on("response", handle_response)

        try:
            print('Acessando PlugShare...')
            page.goto("https://www.plugshare.com/", wait_until="domcontentloaded")
        except Exception as error:
            print(f'Erro ao carregar a página: {error}')
            browser.close()

        try:
            botao1_fechar = page.get_by_role("button", name="cancel")
            botao1_fechar.wait_for(state="visible")
            botao1_fechar.click()
            print('Botão fechar apertado')
        except Exception as error:
            print(f'Botão fechar não apertado: {error}')

        page.wait_for_timeout(15000)
        browser.close()

if __name__ == "__main__":
    run()