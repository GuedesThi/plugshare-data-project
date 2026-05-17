from main import rodar_scrapper_regional

# DEEP SCAN (Zoom 15) - Foco onde a densidade é absurda
# Objetivo: Pegar todos os 75+ postos (120 pontos)
rodar_scrapper_regional(
    lat_n=-22.880, lat_s=-22.990, 
    lon_o=-43.250, lon_l=-43.160, 
    div_lat=10, div_lon=10, zoom=15, name="capital_core_v4"
)