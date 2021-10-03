import geopandas as gpd
coverage = gpd.read_file('fim3outputs_coverage.shp')
coverage_utm = coverage.copy()
coverage_utm.to_crs('EPSG:26914',inplace=True)
## 38.187 m/pixel at zoom level 12:
##  https://wiki.openstreetmap.org/wiki/Zoom_levels
coverage_utm.geometry = coverage_utm.simplify(38.187)
coverage_utm.to_crs(epsg=4326,inplace=True)
coverage_utm.to_file('fim3outputs_coverage_simplified.geojson',driver='GeoJSON')
