# NL2QUERY module

This module serves to transform a natural language (NL) query 
into a structured (dictionary format) query, that can be executed against
a backend of choice. First, the generic interface defines the minimal requirements
any tool has to implement in order to comply to the usage of this module, 
then 3 submodules, namely: named entity recognition (NER), temporal expression recognition (TER), 
and variables and values recognition (Vars_values), implement this interface
with different tools (as described below). Each implementation shows the utility of 
the specific tool to recognize parts of the natural language query, and extract some
crucial information needed for the query specs.

# 1. NL2Query Interface 
This interface is an abstract base class (ABC) that defines the specific annotation types: property, location, 
temporal, target, and the overall QueryAnnotation type. Implementing this interface, 
one must implement all its methods. See an example in MyNL2query.py.
Optionally, a config file can be passed in the constructor, that will be available for a specific implementation.

# 2. Named Entity Recognition (NER)
The named entity recognition submodule tries to detect any generally known entities, such as: organizations, 
people, names, institutions, locations, etc... We provide two implementations: Spacy and Flair.

## 2.1. Spacy
For the well-known NLP tool Spacy, we use the latest 'en_core_web_trf' transformer-based pretrained model.
The results are property and location annotations.

**Attention!** Download the model before usage:
```bash
python -m spacy download en_core_web_trf
```

## 2.2. Flair
Flair is another popular tool to detect named entities. The model 
is automatically donwloaded upon execution. Currently, it generates
only location annotations.

# 3. Temporal Expression Recognition (TER)
Temporal expressions determine a point or an interval in time. We
need to detect them and transform them into a standard format.

## 3.1. Heideltime
Heideltime is a popular TER tool, based on Java and TreeTagger.
This module generates temporal annotations.

**Installation:**
1. Install Java on your machine. 
   
2. Install TreeTagger on your machine. Follow the instructions 
   and download the package specific to your machine from:
   https://www.cis.lmu.de/~schmid/tools/TreeTagger/
   
   Place the package folder under:
   ```bash
   <your_daccs_path>/nlp/nl2query/heideltime
   ```
    
3. Make sure the paths are correctly set in:
   ```bash
   cmd/tree-tagger-english
   ```

4. Test that TreeTagger works. In a terminal, try:
    ```bash
    echo 'Hello world!' | cmd/tree-tagger-english
    ```
   
5. Set TreeTagger path for Heideltime in 'config.props', line 24:
    ```bash
    treeTaggerHome = <your_daccs_path>/nlp/nl2query/heideltime/<your_tagger_package_name>
   ```
   
6. Set paths in 'heideltime_config' for:
   ```bash
   - heideltime jar: de.unihd.dbs.heideltime.standalone.jar
   - heideltime config: config.props
   - treetagger executable: bin/tree-tagger 
   - a temporary file: temp.txt (any name you want)
   ```
   
7. Run TER_heideltime. Make sure that 'heideltime_config'
   is passed in the 'main' as argument
   

# 4. Variables and values recognition
To detect variables and their values (such as 'sensor mode IW'), 
we use pre-processed vocabularies from the following platforms:
PEPS, PAVICS, CMIP6, COPERNICUS, CF STANDARD NAMES.

The pre-processing is done once, and the code is kept in case further
adjustments to the processed vocabulary output or format are needed.

## 4.1. Textsearch
This tool takes a list of words (or a vocabulary) to search for in a text.
When we find a variable name, we must look for the variable value, or the other
way around, and associate the two into one property or target annotation.
CF STANDARD NAMES generate target annotations only.

Still needed: to detect operations, such as 'less than' in the example
'cloud cover less than 10%'.
