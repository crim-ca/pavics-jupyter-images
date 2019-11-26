"""
Download all thedataset from a Thredd server to analyze the metadata
"""
import pickle
import os

# ---- 3rd party libraries -------------------------------------------------------
import threddsclient
import netCDF4


def get_all_ds(catalogue: str):
    refs = set()
    print("Analyzing catalog " + catalogue)
    cat_def = threddsclient.read_url(catalogue)
    # Extraire les catalogues
    for d in cat_def.datasets:
        for c in d.references:
            for x in get_all_ds(c.url):
                refs.add(x)

        # Extraire les datasets
        for ds in d.datasets:
            refs.add(ds.url_path)
    return refs


root = "https://pavics.ouranos.ca/twitcher/ows/proxy/thredds/catalog/birdhouse/catalog.xml"
all_ncs = set()
datadir = os.path.join(os.getcwd(), "data")
all_ncs_file = os.path.join(datadir, "all_ncs.pickle")

if os.path.exists(all_ncs_file):
    # Charger la liste des fichier .nc
    with open(all_ncs_file, 'rb') as f:
        all_ncs = pickle.load(f)

else:
    # Récupérer la liste complète des fichiers .nc du serveur
    for x in get_all_ds(root):
        all_ncs.add(x)

    # Sauvegarder la liste de tous les metadata nc
    if not os.path.exists(datadir):
        os.makedirs(datadir)

    with open(all_ncs_file, 'wb') as f:
        print("Saving the metdata url list to " + os.path.join(datadir, "all_ncs.pickle"))
        pickle.dump(all_ncs, f)

print(str(len(all_ncs)) + " metadata entries recovered from the server.")

# Récupérer tous les metdata des fichiers individuels
print(" Downloading each metadata to store locally.")

i = 0
# for ds in threddsclient.crawl(root, max_depth):
#     i += 1
    # print(ds.name)
    # f = netCDF4.Dataset("https://pavics.ouranos.ca/twitcher/ows/proxy/thredds/dodsC/" + ds.url_path)
    # print(f)
    # print("*** VARIABLES ***")
    # print(f.variables)

print(str(i) + " datasets discovered")
