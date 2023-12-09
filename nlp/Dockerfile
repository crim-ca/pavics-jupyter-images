FROM birdhouse/pavics-jupyter-base:0.4.0

# must update conda env as root, because of a permission error when having pip dependencies in the input yml file
USER root

COPY environment.yml /environment.yml
COPY notebook_config.yml /notebook_config.yml

# update env "birdy"
# use umask 0000 so that package files for the updated environment are usable by the user for the jupyter-conda-extension
RUN umask 0000 && mamba env update -f /environment.yml

# Set the encoding to UTF-8, this is needed for heideltime to work properly
ENV LANG=C.UTF-8

# Download English transformer pipeline from spacy
RUN python -m spacy download en_core_web_trf

# Downloading the ner-large flair model
RUN mkdir flair_models && \
    curl -L -o flair_models/ner-large  https://huggingface.co/flair/ner-english-large/resolve/main/pytorch_model.bin > /dev/null

# Heideltime Tree-tagger Installation
RUN mkdir -p heideltime/tree-tagger-linux-3.2.3 && cd heideltime/tree-tagger-linux-3.2.3 && \
    curl -o tree-tagger-linux-3.2.3.tar.gz  https://www.cis.lmu.de/~schmid/tools/TreeTagger/data/tree-tagger-linux-3.2.3.tar.gz && \
    curl -o tagger-scripts.tar.gz https://www.cis.lmu.de/~schmid/tools/TreeTagger/data/tagger-scripts.tar.gz && \
    curl -o english.par.gz https://www.cis.lmu.de/~schmid/tools/TreeTagger/data/english.par.gz && \
    curl -o install-tagger.sh https://www.cis.lmu.de/~schmid/tools/TreeTagger/data/install-tagger.sh && \
    tar -xvzf tree-tagger-linux-3.2.3.tar.gz  && \
    sh install-tagger.sh && \
    rm tree-tagger-linux-3.2.3.tar.gz tagger-scripts.tar.gz english.par.gz install-tagger.sh

# Download and extract heideltime.standalone.jar
RUN cd heideltime && \   
    curl -L -o heideltime-standalone-2.2.1.tar.gz https://github.com/HeidelTime/heideltime/releases/download/VERSION2.2.1/heideltime-standalone-2.2.1.tar.gz && \
    tar -xzvf heideltime-standalone-2.2.1.tar.gz heideltime-standalone/de.unihd.dbs.heideltime.standalone.jar && \
    mv heideltime-standalone/de.unihd.dbs.heideltime.standalone.jar . && \ 
    rmdir heideltime-standalone && \
    rm heideltime-standalone-2.2.1.tar.gz

# Setup Haskell for Duckling server
# https://github.com/facebook/duckling
RUN curl -sSL https://get.haskellstack.org/ | sh && \
    git clone https://github.com/facebook/duckling && \
    cd duckling && \
    stack build && \
    stack install && \
    rm -fr duckling

# Give read&write permission to jenkins for config
RUN chown -R jenkins heideltime

# Give ownership of the conda cache folder to jenkins, to enable installing packages by the user from JupyterLab
RUN chown -R 1000:1000 /opt/conda/pkgs/cache

# specify user because of problem running start-notebook.sh when being root
USER jenkins
