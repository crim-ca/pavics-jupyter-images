# Temporal Expression Recognition
This readme describes how to fulfill all the necessary requirements
to run the two TER engine: Duckling and Heidltime.

## Duckling
1. Install Docker on your machine.
Follow: https://docs.docker.com/engine/install/
   

2. Check that Docker is installed correctly.
In a terminal run: 
   ```bash
   docker run hello-world
   ```

3. Pull the Duckling Docker image:
    ```bash
    docker pull rasa/duckling
    ```

4. Start the Duckling Engine:
    ```bash
    docker run -p 8000:8000 rasa/duckling
    ```

5. Verify that Duckling is running correctly.
Open https://0.0.0.0:8000 in a browser. It should display 'quack!'
   

6. Now you can run TER_duckling.py

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