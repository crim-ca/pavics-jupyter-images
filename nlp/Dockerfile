FROM birdhouse/pavics-jupyter-base:0.2.1

# must update conda env as root, because of a permission error when having pip dependencies in the input yml file
USER root

COPY environment.yml /environment.yml
COPY ./nl2query /nl2query 
COPY notebook_config.yml /notebook_config.yml

# update env "birdy"
# use umask 0000 so that package files for the updated environment are usable by the user for the jupyter-conda-extension
RUN umask 0000 && conda env update -f /environment.yml

WORKDIR nl2query


# Download spacy model
RUN python -m spacy download en_core_web_trf

# Heideltime Tree-tagger Installation 
RUN cd heideltime && \
    mkdir tree-tagger-linux-3.2.3 && \
    cd tree-tagger-linux-3.2.3 && \
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


# Give read&write permission to jenkins for config
RUN chown -R jenkins .

# specify user because of problem running start-notebook.sh when being root
USER jenkins

