from playwright.sync_api import sync_playwright
import json

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

def print_station_details(s):
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

                    pwr = out.get('kilowatts') or out.get('power') or out.get('amps')
                    pwr_label = f"{float(pwr):.1f}kW" if pwr else "Sob consulta"

                    specs.append(f"Tipo: {conn_id} | Potência: {pwr_label}")

            unique_specs = sorted(list(set(specs)))

            print(f"\n[Eletroposto Detectado]")
            print(f"ID: {s_id} | Nome: {name} | Score: {score}")
            print(f"Endereço: {addr}")
            print(f"Latitude: {lat_dms}")
            print(f"Longitude: {lon_dms}")
            print(f"Acesso: {access_desc} | Tipo: {', '.join(unique_specs)}")
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
                        address = str(station.get('address', '')).upper()
                        city = str(station.get('city', '')).upper()

                        if station.get('access') in [1, 2]:
                            if "RIO DE JANEIRO" in address or " RIO DE JANEIRO" in city or "RJ" in address:
                                print_station_details(station)
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