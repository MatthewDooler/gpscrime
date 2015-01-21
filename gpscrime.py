#!/usr/bin/env python
import os
import re
import csv

if __name__ == "__main__":

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
            lon = row[4]
            lat = row[5]
            type = row[9]
            if type not in crimes[date_key]:
              crimes[date_key][type] = []
            crimes[date_key][type].append((lon, lat))

  for date, types in crimes.items():
    print date
    for type, coords in types.items():
      print "  "+type+": "+str(len(coords))

