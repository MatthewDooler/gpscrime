#!/usr/bin/env python
import os
import re
import csv
import math
import json

# Get data from data.police.uk

def within_radius(search_coordinate, crime_coordinate, radius):

  # If your displacements aren't too great (less than a few kilometers) and you're not right at the poles,
  # use the quick and dirty estimate that 111,111 meters (111.111 km) in the y direction is 1 degree
  # (of latitude) and 111,111 * cos(latitude) meters in the x direction is 1 degree (of longitude).
  search_lat = search_coordinate[0]
  search_lng = search_coordinate[1]
  radius_lat = abs(radius / 111111.0)
  radius_lng = abs(radius / (111111.0 * math.cos(search_lng)))

  crime_lat = crime_coordinate[0]
  crime_lng = crime_coordinate[1]

  if (((crime_lat-search_lat)**2)/(radius_lat**2) + ((crime_lng-search_lng)**2)/(radius_lng**2)) <= 1:
    return True
  else:
    return False

if __name__ == "__main__":

  # var options = {
  #      propertyDetailsMapJsUrl : "/ps/js15007/concat/js_main_v1/propertyDetailsMap.js",
  #      mapOptions : {"attachToElement":".js-map-canvas","latitude":53.47721201921554,"longitude":-2.2481159718307047,"zoom":15,"showPin":true,"tileUri":"/ajax/maps/school-summaries.html","schoolDetailsUri":"/ajax/maps/school-details.html?channel=renting-property-details","showSchools":true,"schoolListContainerSelector":".js-schools-list","schoolMapReducedWidth":"71.8%","showTubeLinesOption":false},
  # console.log(options.mapOptions["latitude"])

  crimes_json_filename = "data/crimes.json"
  search_coordinate = (53.472059309666435,-2.3000610593254676)
  radius = 250 # metres

  
  if os.path.isfile(crimes_json_filename) and os.stat(crimes_json_filename).st_size > 0:
    # The data we want already exists in JSON format
    print "Reading JSON data..."
    crimes_file = open(crimes_json_filename, "r")
    crimes = json.load(crimes_file)
    crimes_file.close()
    print "Done"
  else:
    # Read the data from the original CSV files provided by data.police.uk
    print "Reading raw CSV data..."
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
              if row[0] != "Crime ID" and row[4] != "" and row[5] != "":
                try:
                  lng = float(row[4])
                  lat = float(row[5])
                  type = row[9]
                  if type not in crimes[date_key]:
                    crimes[date_key][type] = []
                  crimes[date_key][type].append((lat, lng))
                except ValueError:
                  print "Error parsing row:",row
    print "Done"

    # Export the data we want in JSON format, so that we don't have to read all the CSV files again next time the program is run
    print "Exporting JSON data to", crimes_json_filename
    with open(crimes_json_filename, "w+") as f:
      f.write(json.dumps(crimes, indent=4, sort_keys=True))
    print "Done"

  # Find number of crimes of each type within the defined radius
  print "Searching for crimes in defined radius..."
  region_crimes = {}
  num_months = len(crimes)
  for date, types in crimes.items():
    for type, coords in types.items():
      if type not in region_crimes:
        region_crimes[type] = 0
      for crime_coordinate in coords:
        if within_radius(search_coordinate, crime_coordinate, radius):
          region_crimes[type] += 1
  print "Done"

  print "Total crimes:"
  for type, crimes in region_crimes.items():
    print "  "+type+":\t"+str(crimes)

  print "Average crimes per month:"
  for type, crimes in region_crimes.items():
    crimes_per_month = round((float(crimes)/num_months), 1)
    print "  "+type+":\t"+str(crimes_per_month)

