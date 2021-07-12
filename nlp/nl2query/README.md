# Temporal Expression Recognition
This readme describes how to fulfill all the necessary requirements
to run the two TER engine:  Heidltime.


## Heideltime

1. Install TreeTagger on your machine. Follow the instructions here:
   https://www.cis.lmu.de/~schmid/tools/TreeTagger/
   
   Place the package folder under:
   ```bash
   <your_daccs_path>/nlp/nl2query/heideltime
   ```
    
2. Make sure the paths are correctly set in:
   ```bash
   cmd/tree-tagger-english
   ```

3. Test that TreeTagger works. In a terminal try:
    ```bash
    echo 'Hello world!' | cmd/tree-tagger-english
    ```
   
4. Set TreeTagger path for Heideltime in 'config.props', line 24:
    ```bash
    treeTaggerHome = <your_daccs_path>/nlp/nl2query/heideltime/<your_tagger_package_name>
   ```
   
5. Set paths in 'heideltime_config' for:
   ```bash
   - heideltime jar: de.unihd.dbs.heideltime.standalone.jar
   - heideltime config: config.props
   - treetagger executable: bin/tree-tagger 
   - a temporary file: temp.txt (any name you want)
   ```
   
6. Run TER_heideltime. Check that 'heideltime_config'
   is passed in the 'main' as argument

   
## Docker Image

1. Set your position to path/to/nlk2query
   ```bash
   cd path/to/nl2query 
    ```

2. Build the docker image 
   ```bash 
    docker build -t nl2query . 
    ```

3. Run the docker image while mounting the folder as volume
   ```bash
    docker run -it --rm -v /path/to/nl2query:/nl2query nl2query <name_file.py> 
    ```
