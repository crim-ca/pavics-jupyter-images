FROM birdhouse/pavics-jupyter-base:0.2.2

# must update conda env as root, because of a permission error when having pip dependencies in the input yml file
USER root

COPY environment.yml /environment.yml

# update env "birdy"
# use umask 0000 so that package files for the updated environment are usable by the user for the jupyter-conda-extension
RUN umask 0000 && conda env update -f /environment.yml

# fix logged warning from GDAL sub-package when accessing Sentinel data via SAFE.ZIP
#   only problematic here when using the 'root' conda env
#   normal user installation with conda activation configures everything correctly
# (https://github.com/conda-forge/gdal-feedstock/issues/83#issue-162911573)
ENV CPL_ZIP_ENCODING=UTF-8

COPY notebook_config.yml /notebook_config.yml

# specify user because of problem running start-notebook.sh when being root
USER jenkins
