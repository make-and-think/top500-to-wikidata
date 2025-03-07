import pywikibot
from pywikibot.page._collections import ClaimCollection

wikidata_properties = {
    "System ID": "P7307",
    "Computer": "P1932",
    "Rank": "P1352",
    "file_time": "P585",  #  Qualifier for Rank
    "Name": "ITEM_LABEL",  # Placeholder for item label, as it's not a property ID
    "Manufacturer": "P176",
    "Country": "P17",
    "Year": "P729", #start time, not "year", but best fitting
    "Segment": "P366",
    "Total Cores": "P1141",  #  Best fit, though context (system vs. processor) is important
    "Power (kW)": "P2791",
    "Processor": "P880",
    "Processor Speed (MHz)": "P2149",  # Qualifier for Processor
    "Cores per Socket": "P1141",   #best fit, but context is important
    "Accelerator/Co-Processor": "P2560",
    "Operating System": "P306",
}

print(wikidata_properties)