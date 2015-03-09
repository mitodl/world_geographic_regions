# world_geographic_regions

UN defined world geographic regions, organized in a single CSV file, suitable for SQL joins and anlaysis.

The output data is provided with a schema file and is suitable for loading into BigQuery, using a command like:

bq load --skip_leading_rows=1 --replace --project_id PROJECT_ID geocode.geographic_regions_by_country geographic_regions_by_country.csv geographic_regions_by_country-schema.json

UN data scraped from http://unstats.un.org/unsd/methods/m49/m49regin.htm
