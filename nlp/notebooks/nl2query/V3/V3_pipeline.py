import json
import os

from nl2query.NL2QueryInterface import (
    LocationAnnotation,
    NL2QueryInterface,
    PropertyAnnotation,
    QueryAnnotationsDict,
    TargetAnnotation,
    TemporalAnnotation
)
from nl2query.V1 import NER_flair, NER_spacy
from nl2query.V2 import V2_pipeline


class V3_pipeline(NL2QueryInterface):

    def __init__(self, v1_config: str = "v1_config.cfg", v2_config: str = "v2_config.cfg"):
        super().__init__(v1_config)
        # use V1 - spacy and V2
        if self.config.get("spacy", "config_file", fallback=None):
            spacy_config_file = self.config.get("spacy", "config_file")
        self.v1_spacy = NER_spacy.NER_spacy(spacy_config_file)
        if self.config.get("flair", "config_file", fallback=None):
            flair_config_file = self.config.get("flair", "config_file")
        self.v1_flair = NER_flair.NER_flair(flair_config_file)  
        self.v2_instance = V2_pipeline.V2_pipeline(v2_config)

    def create_temporal_annotation(self, annotation) -> TemporalAnnotation:
        return self.v2_instance.create_temporal_annotation(annotation)

    def create_location_annotation(self, annotation) -> LocationAnnotation:
        return self.v2_instance.create_location_annotation(annotation)

    def create_property_annotation(self, annotation) -> PropertyAnnotation:
        return self.v2_instance.create_property_annotation(annotation)

    def create_target_annotation(self, annotation) -> TargetAnnotation:
        return self.v2_instance.create_target_annotation(annotation)

    def transform_nl2query(self, nlq: str, verbose:bool=False) -> QueryAnnotationsDict:
        newq = nlq.replace("(", "")
        newq = newq.replace(")", "")
        newq = newq.replace(",", "")
        if verbose:
            print("New query:", newq)
        # collect annotations
        combined_annotations = []
        
        spacy_annotations = self.v1_spacy.transform_nl2query(nlq, verbose)
        v1_results = spacy_annotations.annotations 
        flair_annotations = self.v1_flair.transform_nl2query(nlq, verbose)
        for annot in flair_annotations.annotations:
            # if not already overlap
            overlap = False
            for v1_result in v1_results:
                if range(max(v1_result.position[0], annot.position[0]), min(v1_result.position[-1], annot.position[-1])):
                    overlap = True
            if not overlap:
                v1_results.append(annot)
        
        # temporal annotation 
        # annotate with duckling 
        tempex, newq = self.v2_instance.temporal_annotate(newq, nlq, verbose)
        if len(tempex) > 0:
            combined_annotations += tempex
         
        # take annotations from v1
        v1_temp = [a for a in v1_results if isinstance(a, TemporalAnnotation)]
        # use duckling to fill in other values
        for temp in v1_temp:
            temp_text = temp.text
            # check if overlap with any previous annotations
            if temp_text in newq:
                # add annotation from v1
                tempex, _ = self.v2_instance.temporal_annotate(temp_text, nlq, verbose)
                if len(tempex) > 0:
                    combined_annotations += tempex
                else:
                    combined_annotations.append(temp)
                _, newpos = V2_pipeline.find_spans(temp_text, newq)
                newq = newq[:newpos[0]] + newq[newpos[1]:]
                newq = newq.replace("  ", " ")
                if verbose:
                    print("TEMPEX - V1+V2:\n",combined_annotations[-1])
                    print("New query:", newq)
                    
        # location annotation        
        loc_span, osmnx_annotation = V2_pipeline.osmnx_geocode(self.v2_instance.vdbs, newq)
        if loc_span:
            _, pos = V2_pipeline.find_spans(loc_span, nlq)
            loc = self.create_location_annotation([loc_span, pos, osmnx_annotation])
            combined_annotations.append(loc)
            # remove loc annotations from newq
            _, newpos = V2_pipeline.find_spans(loc.text, newq)
            newq = newq[:newpos[0]] + newq[newpos[1]:]
            newq = newq.replace("  ", " ")
            if verbose:
                print("LOCATION - V2:\n", loc)
                print("New query:", newq)
                
        # take locations from V1
        v1_loc = [a for a in v1_results if isinstance(a, LocationAnnotation)]  
        # use osmnx to fill values
        for loc in v1_loc:
            # print("V1 Loc:", loc.text)
            if loc.text in newq:
                loc_span, osmnx_annotation = V2_pipeline.osmnx_geocode(self.v2_instance.vdbs, loc.text)
                if loc_span:
                    loc = self.create_location_annotation([loc_span, loc.position, osmnx_annotation])
                combined_annotations.append(loc)
                # remove loc annotations from newq
                _, newpos = V2_pipeline.find_spans(loc.text, newq)
                newq = newq[:newpos[0]] + newq[newpos[1]:]
                newq = newq.replace("  ", " ")
                if verbose:
                    print("LOCATION - V1+V2:\n", loc)
                    print("New query:", newq)
        
        newq = V2_pipeline.remove_stopwords(newq)
        if verbose:
            print("\nRemoving stopwords")
            print("New query:", newq)
                        
        # target annotation
        targ_span, targ_results = self.v2_instance.vdbs.query_ngram_target(newq)
        if len(targ_span) > 1 :
            targ_spans, pos = V2_pipeline.find_spans(targ_span, nlq)
            targ_annotation = self.create_target_annotation([targ_spans, pos, targ_results])
            combined_annotations.append(targ_annotation)
            _, newpos = V2_pipeline.find_spans(targ_span, newq)
            newq = newq[:newpos[0]] + newq[newpos[1]:]
            newq = newq.replace("  ", " ")
            if verbose:
                print("TARGET - V2:", targ_annotation)
                print("New query:", newq)
        
        if len(newq) >1:
            # property annotation
            prop_span, prop_results = self.v2_instance.vdbs.query_ngram_prop(newq, threshold=0.8)
            while len(prop_span) > 1:
                prop_spans, pos = V2_pipeline.find_spans(prop_span, nlq)
                prop_annotation = self.create_property_annotation([prop_spans, pos, prop_results])
                combined_annotations.append(prop_annotation)
                _, newpos = V2_pipeline.find_spans(prop_span, newq)
                newq = newq[:newpos[0]] + newq[newpos[1]:]
                newq = newq.replace("  ", " ")
                if verbose:
                    print("PROPERTY - V2:\n", prop_annotation)
                    print("New query:", newq)
                prop_span, prop_results = self.v2_instance.vdbs.query_ngram_prop(newq, threshold=0.82)

        # take prop from V1
        v1_prop = [a for a in v1_results if isinstance(a, PropertyAnnotation)]
        for prop in v1_prop:
            if prop.text in newq:
                # try to find value for this span with low threshold
                prop_span, prop_results = self.v2_instance.vdbs.query_ngram_prop(prop.text, threshold=0.5, verbose=verbose)
                if len(prop_span) > 1:
                    prop = self.create_property_annotation([prop_span, prop.position, prop_results])
                combined_annotations.append(prop)
                if verbose:
                    print("PROPERTY - V1+V2:\n", prop)
           
        # sort and return
        combined_annotations.sort(key=lambda a:(a.position[0][0] \
                                  if isinstance(a.position[0], list) else a.position[0]))
        return QueryAnnotationsDict(query=nlq, annotations=combined_annotations)


    def run_ceda_queries(self, write_out:bool=False):
        """run V3 instance on ceda evaluation dataset"""
        path = os.path.dirname(os.path.realpath(__file__))
        qfile =  os.path.join(path, "../../nl2q_eval/ceda_gold_queries.json")
        struct_results = []
        with open(qfile, 'r', encoding="utf-8") as f:
            qs = json.load(f)
            if 'queries' in qs.keys():
                qlist = qs['queries']
                # iterate over queries
                for q in qlist:
                    print("\n"+q['query'])
                    res = my_instance.transform_nl2query(q['query'])
                    # print(res)
                    struct_results.append(res.to_dict())
            if write_out:
                ofile = os.path.join(path , "v3_ceda_test_results.json")
                with open(ofile, 'w', encoding="utf-8") as f:
                    json.dump({'queries': struct_results}, f, indent=2)
        return struct_results


if __name__ == "__main__":
    # call my nl2query class
    v1_config = "nl2query/V1/v1_config.cfg"
    v2_config = "nl2query/V2/v2_config.cfg"
    my_instance = V3_pipeline(v1_config, v2_config)
    # get the structured query from the nl query
    query = "Annual downward UV radiation in uk from today to 2100"
    structq = my_instance.transform_nl2query(query)
    print("\nStructured query: \n", structq)
    
    my_instance.run_ceda_queries(write_out=True)
