import pywikibot
import pprint

# --- Configuration ---
wikidata_site = pywikibot.Site("wikidata", "wikidata")
wikidata_repo = wikidata_site.data_repository()
test_wikidata_site = pywikibot.Site("test", "wikidata")
test_wikidata_repo = test_wikidata_site.data_repository()

test_wikidata_repo.login()  # Ensure you're logged in

properties_to_copy = [
    "P7307",
    "P1932",
    "P1352",
    "P585",
    "P176",
    "P17",
    "P729",
    "P366",
    "P1141",
    "P2791",
    "P880",
    "P2149",
    "P2560",
    "P306"
]

new_property_ids = {}  # Dictionary to store {source_property_id: new_property_id}

for source_property_id in properties_to_copy:
    try:
        # Load the existing property
        source_property = pywikibot.PropertyPage(wikidata_repo, source_property_id)
        source_property.get()  # Load the data

        # Copy relevant data
        new_property_data = {
            'labels': source_property.labels,
            'descriptions': source_property.descriptions,
            'aliases': source_property.aliases,
            'datatype': source_property.type
        }

        # Create the new property
        new_property = pywikibot.PropertyPage(test_wikidata_repo, datatype=new_property_data["datatype"])
        summary = "Creating new property based on " + source_property_id
        new_property.editEntity(data=new_property_data, summary=summary)

        # Store the new property ID
        new_property_ids[source_property_id] = new_property.getID()
        print(f"Property {source_property_id} copied to test environment as {new_property.getID()}")

    except pywikibot.exceptions.OtherPageSaveError as e:
        # Check for label conflict
        if "wikibase-validator-label-conflict" in str(e):
            print(f"Skipping property {source_property_id} due to label conflict with an existing property.")
            new_property_ids[source_property_id] = None  # Mark as skipped
        else:
            # Other save errors - re-raise or handle differently
            print(f"Error copying property {source_property_id}: {e}")
            new_property_ids[source_property_id] = None
    except Exception as e:
        print(f"Error copying property {source_property_id}: {e}")
        new_property_ids[source_property_id] = None

# --- Output the mapping ---
pprint.pprint(new_property_ids)

# String representation
new_property_ids_str = str(new_property_ids)
print("\nString Representation:")
print(new_property_ids_str)