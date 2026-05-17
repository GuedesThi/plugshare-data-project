from main import rodar_scrapper_regional
# Foco: Petrópolis, Teresópolis e Friburgo
rodar_scrapper_regional(
    lat_n=-22.20, lat_s=-22.60, 
    lon_o=-43.30, lon_l=-42.40, 
    div_lat=6, div_lon=10, zoom=14, name="serra"
)