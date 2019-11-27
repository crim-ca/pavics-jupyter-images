"""
Download all thedataset from a Thredd server to analyze the metadata
"""
import pickle
import os
import time

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
all_md_files = os.path.join(datadir, "all_md_files.pickle")
all_md = dict()

if os.path.exists(all_md_files):
    # Charger la liste
    with open(all_md_files, 'rb') as f:
        all_md = pickle.load(f)

# Télécharger tous les fichiers de méta
if not len(all_md) == len(all_ncs):
    cpt_new = 0
    for x in all_ncs:
        if x not in all_md:
            try:
                ds = netCDF4.Dataset(
                    "https://pavics.ouranos.ca/twitcher/ows/proxy/thredds/dodsC/" + x)
                print(len(ds.variables))
                time.sleep(.1)
                cpt_new += 1
                new_ds = vars(ds)
                new_ds["variables"] = dict()
                for v in ds.variables:
                    new_ds["variables"][v] = vars(ds.variables[v])
                all_md[x] = new_ds
                ds.close()
            except Exception as ex:
                print("Cannot load : " + x)
                print(ex)
                if ex.errno is not -37:
                    all_md[x] = "##Cannot load## : " + str(ex)
                else:
                    time.sleep(5)

            # Save each N file
            if cpt_new % 5 == 0:
                with open(all_md_files, 'wb') as f:
                    print("Checkpoint... (" + str(len(all_md)) + ")")
                    pickle.dump(all_md, f)
