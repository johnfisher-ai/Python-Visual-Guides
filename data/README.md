# data

Datasets used by the notebooks, shared across guides rather than duplicated per guide.

A notebook should load from a raw GitHub URL so it works in Colab without a clone.

## nordic-countries.geojson

The outlines of Denmark, Finland, Norway, Russia and Sweden, for the GeoPandas, Deep Dive guide.
Made with Natural Earth. The outlines come from Natural Earth's 1:50m Admin 0 countries layer,
which is in the public domain (https://www.naturalearthdata.com/about/terms-of-use/), with six of
its columns: `ADMIN`, `ADM0_A3`, `ISO_A3`, `POP_EST`, `POP_YEAR` and `CONTINENT`. They are clipped
to longitudes −2 to 42 and latitudes 53 to 82, which cuts Russia at 42 degrees east, and written in
WGS 84 (EPSG:4326) with coordinates rounded to four decimal places, about 10 meters. Natural
Earth gives Norway an `ISO_A3` of `-99`, and the file keeps it as Natural Earth has it.
