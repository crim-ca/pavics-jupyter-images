from nlp.notebooks.nl2query.NL2QueryInterface import *
import os.path
from subprocess import check_output
from xml.etree import ElementTree
from datetime import datetime

class TER_heideltime(NL2QueryInterface):
    """ Heideltime implementation of the NL2query interface"""

    def __init__(self, config: str = None):
        super().__init__(config)
        # check heideltime and treetagger
        self.cwd = os.getcwd()
        self.heideltime_jar = self.cwd+self.config.get('heideltime', 'heideltime_jar')
        self.heideltime_config = self.cwd+self.config.get('heideltime', "heideltime_config")
        self.treetagger = self.cwd+self.config.get('heideltime', "tree-tagger")
        self.tempfile = self.cwd+self.config.get('heideltime', "tempfile")
        if not os.path.exists(self.heideltime_jar) or \
            not os.path.exists(self.heideltime_config) or \
                not os.path.exists(self.treetagger):
            raise Exception("Did not find all necessary HeidelTime files! Please copy them from:"
                  "https://github.com/amineabdaoui/python-heideltime, and install your"
                  "machine-specific treetagger from : https://www.cis.lmu.de/~schmid/tools/TreeTagger/")


    def call_heideltime(self, nlq: str):
        # write nlq string to temp file
        try:
            with open(self.tempfile, "w") as tf:
                tf.write(nlq)
                tf.close()
            out = check_output(['java', '-jar', self.heideltime_jar,
                                self.tempfile,
                                '-it',
                                '-l', 'english',
                                '-t', 'colloquial',
                                '-c', self.heideltime_config])
            # remove tempfile
            os.remove(self.tempfile)
            # decode output and read it as xml
            out_tree = ElementTree.fromstring(out.decode())
            # print("Heideltime returned:\n", out.decode())

            if out_tree.tag == "TimeML":
                # if timeml tag is found
                found = []
                for item in out_tree.iter():
                    if item.tag in ["TIMEX3", "TIMEX3INTERVAL"]:
                        item.text = "".join(item.itertext())
                        found.append(item)
                return found
            else:
                print("Error finding temporal annotations in output: ", out.decode())
                return []
        except Exception as e:
            print(e)
            print("- Make sure your treetagger installation is correct for your machine: "
                  "https://www.cis.lmu.de/~schmid/tools/TreeTagger/."
                  "Check that the path in cmd/tree-tagger-english script are correct. "
                  "Try Treetagger with cmd: \n"
                  "echo 'Hello there' | cmd/tree-tagger-english. \n"
                  "- Make sure you have JVM installed \n"
                  "- Make sure heideltime is correct. Set treetagger's path in config.props. Try calling"
                  "java -jar de.unihd.dbs.heideltime.standalone.jar temp.txt -l english -c config.props")
            exit()

    def create_property_annotation(self, annotation) -> PropertyAnnotation:
        # take annotation given by the engine
        # and create appropriate typeddict annotation
        # filling in each slot as required

        return PropertyAnnotation(text=annotation.text, position=[annotation.start_char, annotation.end_char],
                                  name="", value="", value_type="", operation="")

    def create_location_annotation(self, annotation) -> LocationAnnotation:
        # get gejson of location
        geojson = {}
        return LocationAnnotation(text=annotation.text, position=[annotation.start_char, annotation.end_char],
                                  matching_type="", name=annotation.text, value=geojson)

    def create_temporal_annotation(self, annotation) -> TemporalAnnotation:
        # get standard dateformat from text
        t_type = "point"
        dateval = ""
        if annotation.tag == "TIMEX3":
            datestr = annotation.attrib['value']
            datetype = annotation.attrib['type']
            if datetype == "DURATION":
                if 'start' and ' end' in datestr:
                    dateval = {"start": datetime.strptime(datestr['start']).strftime("%Y-%m-%dT%H:%M:%S") +"Z",
                               "end": datetime.strptime(datestr['end']).strftime("%Y-%m-%dT%H:%M:%S")+"Z"}
                elif datestr.startswith('P'):
                    dateval = {"start": "#currentdate-"+datestr[1:], "end": "#currentdate"}
                else:
                    print("Duration not processed: ", datestr)
                    dateval = {"start": "", "end": ""}
                t_type = "range"
            elif datetype in ["DATE", "TIME"]:
                # convert here any date string detected by heideltime to
                # the format YYYY-MM-DDTHH:MM:SSZ
                # but we don't know the format
                if '-' in datestr:
                    if datestr.count('-')>1:
                        dateval = datetime.strptime(datestr, "%Y-%m-%d")
                    else:
                        dateval = datetime.strptime(datestr, "%Y-%m")
                elif str(datestr).isnumeric():
                    dateval = datetime.strptime(datestr, '%Y')
                else:
                    dateval = None
                if dateval:
                    print("HEIDELTIME datetime:", dateval)
                    dateval = dateval.strftime("%Y-%m-%dT%H:%M:%S") +"Z"
                else:
                    print("Date time not processed:", datestr)
                    dateval = {"start": "", "end": ""}
                t_type = "point"
        elif annotation.tag == "TIMEX3INTERVAL":
            start = annotation.attrib['earliestBegin'] + "Z"
            end = annotation.attrib['latestEnd'] + "Z"
            t_type = "range"
            dateval = {"start": start, "end": end}
        return TemporalAnnotation(text=annotation.text, position=[annotation.attrib['start'], annotation.attrib['end']],
                                  tempex_type=t_type, target="dataDate", value=dateval)

    def create_target_annotation(self, annotation) -> TargetAnnotation:
        return TargetAnnotation(text=annotation['text'],  position=[annotation['start'], annotation['end']],
                                name=[""])

    def transform_nl2query(self, nlq: str) -> QueryAnnotationsDict:
        # collect annotations in a list of typed dicts
        annot_dicts = []
        # get annotations from my engine
        annots = self.call_heideltime(nlq)#, reference_time=str(datetime.datetime.today()))
        for timex3 in annots:
            print("HEIDELTIME TER:",timex3.text, timex3.tag, timex3.attrib)
            # we have to add span position
            if timex3.text:
                start_pos = nlq.index(timex3.text)
                end_pos = start_pos + len(timex3.text)
                timex3.attrib.update({"start": start_pos, "end": end_pos})
            else:
                print("Warning! Annotation with empty text.")
                timex3.attrib.update({"start": -1, "end": -1})
            annot_dicts.append(self.create_temporal_annotation(timex3))
        # return a query annotations typed dict as required
        return QueryAnnotationsDict(query=nlq, annotations=annot_dicts)


if __name__ == "__main__":
    query = "Sentinel-2 over Ottawa from april to september 2020 with cloud cover lower than 10%"
    # call my nl2query class
    my_instance = TER_heideltime('heideltime_config.cfg')
    # get the structured query from the nl query
    structq = my_instance.transform_nl2query(query)
    print("Structured query: ", structq)
