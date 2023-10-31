FROM birdhouse/pavics-jupyter-base:0.5.0

# must update conda env as root, because of a permission error when having pip dependencies in the input yml file
USER root

COPY environment.yml /environment.yml
# COPY requirements.txt /requirements.txt
# update env "birdy"
# use umask 0000 so that package files for the updated environment are usable by the user for the jupyter-conda-extension
RUN umask 0000 && mamba env update -f /environment.yml \
    && mamba clean -a

# Give ownership of the conda cache folder to jenkins, to enable installing packages by the user from JupyterLab
RUN mkdir /opt/conda/pkgs/cache && chown -R 1000:1000 /opt/conda/pkgs/cache

# fix logged warning from GDAL sub-package when accessing Sentinel data via SAFE.ZIP
#   only problematic here when using the 'root' conda env
#   normal user installation with conda activation configures everything correctly
# (https://github.com/conda-forge/gdal-feedstock/issues/83#issue-162911573)
ENV CPL_ZIP_ENCODING=UTF-8

COPY notebook_config.yml /notebook_config.yml

# specify user because of problem running start-notebook.sh when being root
USER jenkins
