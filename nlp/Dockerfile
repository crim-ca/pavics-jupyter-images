FROM birdhouse/pavics-jupyter-base:0.2.1

# must update conda env as root, because of a permission error when having pip dependencies in the input yml file
USER root

COPY environment.yml /environment.yml

# update env "birdy"
# use umask 0000 so that package files for the updated environment are usable by the user for the jupyter-conda-extension
RUN umask 0000 && conda env update -f /environment.yml

COPY notebook_config.yml /notebook_config.yml

# specify user because of problem running start-notebook.sh when being root
USER jenkins

