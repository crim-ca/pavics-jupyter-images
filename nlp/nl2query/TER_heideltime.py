from NL2query import *
import os.path
from subprocess import check_output
from xml.etree import ElementTree
from datetime import datetime
from dateutil import parser

class TER_heideltime(NL2Query):
    """ Heideltime implementation of the NL2query interface"""

    def __init__(self, config: str = None):
        NL2Query.__init__(self, config)
        # check heideltime and treetagger
        self.heideltime_jar = "heideltime/de.unihd.dbs.heideltime.standalone.jar"
        self.heideltime_config = "heideltime/config.props"
        self.treetagger = "heideltime/tree-tagger-linux-3.2.3/bin/tree-tagger"
        self.tempfile = "heideltime/temp.txt"
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
                                '-l', 'english',
                                '-t', 'colloquial',
                                '-c', self.heideltime_config])
            # remove tempfile
            os.remove(self.tempfile)
            # decode output and read it as xml
            out_tree = ElementTree.fromstring(out.decode())
            if out_tree.tag == "TimeML":
                # if timeml tag is found
                return out_tree.findall('TIMEX3')
            else:
                print("Error finding temporal annotations in output: ", out.decode())
                return []
        except Exception:
            print("- Make sure your treetagger installation is correct for your machine: "
                  "https://www.cis.lmu.de/~schmid/tools/TreeTagger/."
                  "Check that the path in cmd/tree-tagger-english script are correct. "
                  "Try Treetagger with cmd: \n"
                  "echo 'Hello there' | cmd/tree-tagger-english. \n"
                  "- Make sure you have JVM installed \n"
                  "- Make sure heideltime is correct. Set treetagger's path in config.props. Try calling"
                  "java -jar de.unihd.dbs.heideltime.standalone.jar temp.txt -l english -c config.props")


    def create_property_annotation(self, annotation) -> PropertyAnnotation:
        # take annotation given by the engine
        # and create appropriate typeddict annotation
        # filling in each slot as required

        return PropertyAnnotation(text=annotation.text, type="property", position=[annotation.start_char, annotation.end_char],
                                  name="", value="", value_type="", operation="")

    def create_location_annotation(self, annotation) -> LocationAnnotation:
        # get gejson of location
        geojson = {}
        return LocationAnnotation(text=annotation.text, type="location", position=[annotation.start_char, annotation.end_char],
                                  matchingType="", name=annotation.text, value=geojson)

    def create_temporal_annotation(self, annotation) -> TemporalAnnotation:
        # get standard dateformat from text
        datestr = annotation.attrib['value']
        datetype = annotation.attrib['type']
        if datetype == "DURATION":
            datetm = {"start": datetime.strptime(datestr['start']).strftime("YYYY-MM-DDTHH:MM:SS"),
                      "end": datetime.strptime(datestr['end']).strftime("YYYY-MM-DDTHH:MM:SS")}
            t_type = "range"
        elif datetype in ["DATE", "TIME"]:
            # convert here any date string detected by heideltime to
            # the format YYYY-MM-DDTHH:MM:SSZ
            # but we don't know the format
            #datetm = datetime.strptime(datestr, detected_format).strftime("YYYY-MM-DDTHH:MM:SS")
            t_type = "point"
        return TemporalAnnotation(text=annotation.text, type="tempex", position=[annotation.attrib['start'], annotation.attrib['end']],
                                  tempex_type=t_type, target="dataDate", value=datestr)

    def create_target_annotation(self, annotation) -> TargetAnnotation:
        return TargetAnnotation(text=annotation['text'], type="target", position=[annotation['start'], annotation['end']],
                                name=[""])

    def transform_nl2query(self, nlq: str) -> QueryAnnotationsDict:
        # collect annotations in a list of typed dicts
        annot_dicts = []
        # get annotations from my engine
        annots = self.call_heideltime(nlq)#, reference_time=str(datetime.datetime.today()))
        for timex3 in annots:
            # we have to add span position
            start_pos = nlq.index(timex3.text)
            end_pos = start_pos + len(timex3.text)
            timex3.attrib.update({"start": start_pos, "end": end_pos})
            print(timex3.text, timex3.attrib)
            annot_dicts.append(self.create_temporal_annotation(timex3))
        # return a query annotations typed dict as required
        return QueryAnnotationsDict(query=nlq, annotations=annot_dicts)


if __name__ == "__main__":
    query = "Sentinel-2 over Ottawa from april to september 2020 with cloud cover lower than 10%"
    # call my nl2query class
    my_instance = TER_heideltime()
    # get the structured query from the nl query
    structq = my_instance.transform_nl2query(query)
    print("Structured query: ", structq)
