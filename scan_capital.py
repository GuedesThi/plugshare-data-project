from main import rodar_scrapper_regional

# ==============================================================================
# EIXO 1: CENTRO & ZONA SUL (O Coração da Rede)
# Abrange: Centro, Porto, Botafogo, Copacabana, Ipanema, Leblon, Lagoa e Flamengo.
# ==============================================================================
rodar_scrapper_regional(
    lat_n=-22.89, lat_s=-23.01, 
    lon_o=-43.24, lon_l=-43.15, 
    div_lat=10, div_lon=10, zoom=15, name="capital_centro_zs"
)

# ==============================================================================
# EIXO 2: TIJUCA & MARACANÃ (Adensamento Urbano)
# Abrange: Tijuca, Maracanã, Vila Isabel, Grajaú e São Cristóvão.
# ==============================================================================
rodar_scrapper_regional(
    lat_n=-22.90, lat_s=-22.95, 
    lon_o=-43.28, lon_l=-43.21, 
    div_lat=6, div_lon=6, zoom=15, name="capital_tijuca"
)

# ==============================================================================
# EIXO 3: BARRA DA TIJUCA (Hub Comercial)
# Abrange: Barra, Shopping Village Mall, BarraShopping e arredores.
# ==============================================================================
rodar_scrapper_regional(
    lat_n=-22.96, lat_s=-23.03, 
    lon_o=-43.43, lon_l=-43.30, 
    div_lat=8, div_lon=8, zoom=15, name="capital_barra"
)

# ==============================================================================
# EIXO 4: RECREIO (Expansão Zona Oeste)
# Abrange: Recreio dos Bandeirantes e shoppings da região.
# ==============================================================================
rodar_scrapper_regional(
    lat_n=-23.00, lat_s=-23.05, 
    lon_o=-43.53, lon_l=-43.43, 
    div_lat=5, div_lon=6, zoom=15, name="capital_recreio"
)