from main import rodar_scrapper_regional

# ==============================================================================
# FOCO 1: EIXO NOVA IGUAÇU / QUEIMADOS (Via Dutra & Shoppings)
# Abrange: TopShopping, Shopping Nova Iguaçu, Centros e Postos na Dutra.
# ==============================================================================
rodar_scrapper_regional(
    lat_n=-22.72, lat_s=-22.78, 
    lon_o=-43.60, lon_l=-43.40, 
    div_lat=6, div_lon=8, zoom=15, name="baixada_ni_queimados"
)

# ==============================================================================
# FOCO 2: DUQUE DE CAXIAS (Centro & Washington Luiz)
# Abrange: Caxias Shopping, Outlet Premium, Centro e o eixo logístico da BR-040.
# ==============================================================================
rodar_scrapper_regional(
    lat_n=-22.65, lat_s=-22.80, 
    lon_o=-43.35, lon_l=-43.20, 
    div_lat=8, div_lon=6, zoom=15, name="baixada_caxias_prof"
)

# ==============================================================================
# FOCO 3: SÃO JOÃO DE MERITI / NILÓPOLIS (Densidade Urbana)
# Abrange: Shopping Grande Rio e áreas centrais de alta circulação.
# ==============================================================================
rodar_scrapper_regional(
    lat_n=-22.78, lat_s=-22.82, 
    lon_o=-43.40, lon_l=-43.30, 
    div_lat=4, div_lon=5, zoom=15, name="baixada_meriti_nilopolis"
)

# ==============================================================================
# FOCO 4: EIXO RODOVIÁRIO SEROPÉDICA (Estradas)
# Foco específico nos postos de estrada que você mencionou.
# ==============================================================================
rodar_scrapper_regional(
    lat_n=-22.73, lat_s=-22.82, 
    lon_o=-43.75, lon_l=-43.65, 
    div_lat=6, div_lon=6, zoom=15, name="baixada_seropedica_road"
)