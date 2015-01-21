#!/usr/bin/env python
import os
import re
import csv
import math

def within_radius(search_coordinate, crime_coordinate, radius):

  # If your displacements aren't too great (less than a few kilometers) and you're not right at the poles,
  # use the quick and dirty estimate that 111,111 meters (111.111 km) in the y direction is 1 degree
  # (of latitude) and 111,111 * cos(latitude) meters in the x direction is 1 degree (of longitude).
  search_lat = search_coordinate[0]
  search_lng = search_coordinate[1]
  radius_lat = abs(radius / 111111.0)
  radius_lng = abs(radius / (111111.0 * math.cos(search_lng)))

  search_lat_min = search_lat - radius_lat
  search_lat_max = search_lat + radius_lat
  search_lng_min = search_lng - radius_lng
  search_lng_max = search_lng + radius_lng

  crime_lat = crime_coordinate[0]
  crime_lng = crime_coordinate[1]
  # TODO: this is an estimate, as it checks a box not a circle
  if crime_lat > search_lat_min and crime_lat < search_lat_max and crime_lng > search_lng_min and crime_lng < search_lng_max:
    return True
  else:
    return False


if __name__ == "__main__":

  # var options = {
  #      propertyDetailsMapJsUrl : "/ps/js15007/concat/js_main_v1/propertyDetailsMap.js",
  #      mapOptions : {"attachToElement":".js-map-canvas","latitude":53.47721201921554,"longitude":-2.2481159718307047,"zoom":15,"showPin":true,"tileUri":"/ajax/maps/school-summaries.html","schoolDetailsUri":"/ajax/maps/school-details.html?channel=renting-property-details","showSchools":true,"schoolListContainerSelector":".js-schools-list","schoolMapReducedWidth":"71.8%","showTubeLinesOption":false},
  # console.log(options.mapOptions["latitude"])

  search_coordinate = (53.47721201921554, -2.2481159718307047)
  radius = 150 # metres

  crimes = {}
  for dirname, dirnames, filenames in os.walk('data'):
    for filename in filenames:
      m = re.search("(\d+)-(\d+)-(.*)\.csv", filename)
      if m:
        groups = m.groups()
        year = str(groups[0])
        month = str(groups[1])
        filepath = os.path.join(dirname, filename)
        date_key = year+"-"+month
        if date_key not in crimes:
          crimes[date_key] = {}
        with open(filepath, 'rb') as f:
          reader = csv.reader(f)
          for row in reader:
            if row[0] != "Crime ID":
              lng = float(row[4])
              lat = float(row[5])
              type = row[9]
              if type not in crimes[date_key]:
                crimes[date_key][type] = []
              crimes[date_key][type].append((lat, lng))

  # Find number of crimes of each type within the defined radius
  region_crimes = {}
  num_months = len(crimes)
  for date, types in crimes.items():
    for type, coords in types.items():
      if type not in region_crimes:
        region_crimes[type] = 0
      for crime_coordinate in coords:
        if within_radius(search_coordinate, crime_coordinate, radius):
          region_crimes[type] += 1

  for type, crimes in region_crimes.items():
    crimes_per_month = round((float(crimes)/num_months), 1)
    print type, crimes, crimes_per_month

