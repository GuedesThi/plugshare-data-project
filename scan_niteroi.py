from main import rodar_scrapper_regional

# ==============================================================================
# EIXO 1: CENTRO, ICARAÍ & SÃO FRANCISCO (Densidade Máxima)
# Abrange: Centro, Icaraí, Santa Rosa, São Francisco, Jurujuba e Ingá.
# ==============================================================================
rodar_scrapper_regional(
    lat_n=-22.88, lat_s=-22.94, 
    lon_o=-43.13, lon_l=-43.08, 
    div_lat=8, div_lon=8, zoom=15, name="niteroi_centro_icarai"
)

# ==============================================================================
# EIXO 2: REGIÃO OCEÂNICA (Shoppings e Condomínios)
# Abrange: Piratininga, Itaipu, Itacoatiara e Camboinhas.
# ==============================================================================
rodar_scrapper_regional(
    lat_n=-22.93, lat_s=-22.97, 
    lon_o=-43.08, lon_l=-43.02, 
    div_lat=6, div_lon=6, zoom=15, name="niteroi_oceanica"
)

# ==============================================================================
# EIXO 3: PENDOTIBA & ACESSOS (Conexões)
# Abrange: Largo da Batalha, Badu, Maria Paula e conexão com São Gonçalo.
# ==============================================================================
rodar_scrapper_regional(
    lat_n=-22.85, lat_s=-22.92, 
    lon_o=-43.08, lon_l=-43.00, 
    div_lat=5, div_lon=5, zoom=15, name="niteroi_pendotiba"
)