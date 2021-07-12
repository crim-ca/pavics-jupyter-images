from NL2QueryInterface import *
from textsearch import TextSearch
from vocab.Vocabulary import Vocabulary

class Vars_values_textsearch(NL2QueryInterface):

    def __init__(self, config: str = None):
        super().__init__(config)
        # TextSearch params:
        #   -  case: one of "ignore", "insensitive", "sensitive", "smart"
        #   -  returns: one of 'match', 'norm', 'object' or a custom class
        if self.config:
            self.ts = TextSearch(case=self.config['textsearch']['case'],
                                 returns=self.config['textsearch']['returns'])
            self.ts_climate = TextSearch(case=self.config['textsearch']['case'],
                                returns=self.config['textsearch']['returns'])
            # get vocabs
            self.vocabs = {'cmip6': Vocabulary(self.config['vocabs']['cmip6']),
                           'peps': Vocabulary(self.config['vocabs']['peps']),
                           'copernicus': Vocabulary(self.config['vocabs']['copernicus']),
                           'paviccs': Vocabulary(self.config['vocabs']['peps'])
                           }
            self.vocab_climate = {'cf_standard_names': Vocabulary(self.config['vocabs']['cf_standard_names'])}
        else:
            print("Please define vocabulary file paths in a config, and "
                  "pass it to the constructor!")
            exit()
        self.words = {}
        for key in self.vocabs:
            self.words[key] = self.vocabs[key].get_vars_list()

        # create list of words, vars and values
        self.vars_list = []
        self.values_list = []
        # add vocabs to textsearch
        for key in self.vocabs:
            print("Adding to textsearch engine vocabulary words for: ", key)
            self.vars_list += self.vocabs[key].get_vars_list()
            self.values_list += self.vocabs[key].get_values_list()
        self.words_list = self.vars_list + self.values_list
        if not self.words_list:
            print("Error adding words to the vocabulary!")
        else:
            self.ts.add(self.words_list)

        # same for climate
        self.vars_climate_list = []
        self.values_climate_list = []
        # add vocabs to textsearch
        for key in self.vocab_climate:
            print("Adding to textsearch engine vocabulary words for: ", key)
            self.vars_climate_list += self.vocab_climate[key].get_vars_list()
            self.values_climate_list += self.vocab_climate[key].get_values_list()
        self.words_climate_list = self.vars_climate_list + self.values_climate_list
        if not self.words_climate_list:
            print("Error adding words to the vocabulary!")
        else:
            self.ts_climate.add(self.words_climate_list)
        print("Vocabularies successfully added to textsearch engine!")

    def create_location_annotation(self, annotation: Any) -> LocationAnnotation:
        pass

    def create_property_annotation(self, annotation: Any) -> PropertyAnnotation:
        # if matched string is the variable, put it in name, and value in value
        name = ""
        value = ""
        if annotation.match in self.vars_list:
            name = annotation.norm
            # value is the detected value
        # if matched string is a value to a variable, put it in value,
        # and find variable name in vocab
        if annotation.match in self.values_list:
            value = annotation.norm
            for vocab in self.vocabs:
                name = self.vocabs[vocab].find_var_of_value(value)
                if name:
                    break

        if value.isdigit():
            value_type = "integer"
            value = int(value)
        else:
            value_type = "string"
        return PropertyAnnotation(text=annotation.match, position=[annotation.start, annotation.end],
                                  name=name, value=value, value_type=value_type, operation="eq")

    def create_target_annotation(self, annotation: Any) -> TargetAnnotation:
        name = []
        # if it's a variable, find the target name
        if annotation.norm in self.vars_climate_list:
            value = annotation.norm
            for vocab in self.vocab_climate:
                name = self.vocab_climate[vocab].find_value_of_var(value)
                if name:
                    break

        # if matched string is a value to a variable, put it in target name
        if annotation.match in self.values_climate_list:
            name = annotation.norm

        return TargetAnnotation(text=annotation.match, position=[annotation.start, annotation.end],
                                name=name)

    def create_temporal_annotation(self, annotation: Any) -> TemporalAnnotation:
        pass

    def transform_nl2query(self, nlq: str) -> QueryAnnotationsDict:
        print("Searching vocabulary words...")
        annotations_list = []
        for result in self.ts.findall(nlq):
            print(result)
            annotations_list.append(self.create_property_annotation(result))
        for result in self.ts_climate.findall(nlq):
            print(result)
            annotations_list.append(self.create_target_annotation(result))
        return QueryAnnotationsDict(nlq, annotations_list)


if __name__ == "__main__":
    myvarval = Vars_values_textsearch("varval_config.cfg")
    nlquery = "Sentinel-2 over Ottawa from april to september 2020 with cloud cover lower than 10%"
    nlquery = "I want the CO2 concentrations and total canopy water storage " \
              "used to force the CMIP6 models cell area in ScenarioMIP"
    structq = myvarval.transform_nl2query(nlq=nlquery)
    print("Structured query: ", structq)

