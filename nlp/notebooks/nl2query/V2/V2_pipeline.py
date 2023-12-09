import time

import datetime
import json
import os
import re
import sys
import subprocess
from typing import List, Optional

import nltk
import osmnx as ox
import requests

from nl2query.NL2QueryInterface import (
    LocationAnnotation,
    NL2QueryInterface,
    PropertyAnnotation,
    QueryAnnotationsDict,
    TargetAnnotation,
    TemporalAnnotation
)
from nl2query.V2.Vdb_simsearch import Vdb_simsearch
from typedefs import JSON

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
from nltk.corpus import stopwords


def find_spans(span: str, query: str):
    """Find a span  in a query.
    Return the spans or a list of spans 
    in the case of split spans and 
    their positions in the query."""
    # split span case
    if span not in query:
        pos = []
        spans = []
        splits = span.split(" ")
        ostart = -1
        oend = -1
        for split in splits:
            if split not in query:
                print("NOT FOUND IN QUERY:", split, query, splits, span)
            start = query.index(split)
            end = start + len(split)
            if span.startswith(split):
                # first iteration
                ostart = start
                oend = end
            else:
                # if continuous span
                if oend + 1 == start:
                    oend = end
                elif ostart != oend:
                    # otherwise append to poisiton and span list
                    pos.append([ostart, oend])
                    spans.append(query[ostart:oend])
                    ostart = start
                    oend = end
        if ostart != oend:
            spans.append(query[ostart:oend])
            pos.append([ostart, oend])
    else:
        pad_span = " " + span + " "
        if pad_span in query:
            start = query.index(pad_span)+1
        else:
            if query.startswith(span):
                start = 0
            elif query.endswith(span):
                start = len(query) - len(span)
            else:
                start = query.index(span)
                # print("WRONG span search in query!", span, query)
        end = start + len(span)
        pos = [start, end]
        spans = span
    return spans, pos


def remove_stopwords(text:str):
    """Given a string, remove 
    the stopwords with nltk.
    Return the filtered text"""
    stop_words = set(stopwords.words('english'))
    filtered_text = ' '.join([word for word in text.split() if word.lower() not in stop_words])
    return filtered_text


def osmnx_geocode(vdb: Vdb_simsearch, query: str, threshold: float = 0.7, policy: str = 'length'):
    """location geocoding service
    that queries every 1 and 2-gram tokens
    and returns a result above the threshold (default 0.7)
    and highest score if policy=score
    or highest length if policy=length (default)."""
    query_tokens,_ = vdb.query_ngram_target(query, 2)
    # query by 1-gram and 2-gram tokens
    importance = 0
    max_gdf = None
    max_token = None
    max_len = 0
    for token in query_tokens:
        try:
            gdf = ox.geocode_to_gdf(token)
            if len(gdf) > 0 and gdf['class'].iloc[0]in ['boundary', 'city', 'country', 'place']:
                gdf_imp = gdf['importance'].iloc[0] 
                if policy == "score" and gdf_imp > threshold and gdf_imp > importance:
                    importance = gdf['importance'][0]
                    max_token = token
                    max_gdf = gdf
                elif policy=="length" and gdf_imp > threshold and len(token) > max_len:
                    max_token = token
                    max_gdf = gdf
                    max_len = len(token)
        except:
            continue
    return (max_token, max_gdf)


class V2_pipeline(NL2QueryInterface):

    def __init__(self, config: str = "v2_config.cfg"):
        super().__init__(os.path.join(os.path.dirname(os.path.realpath(__file__)),config))
        # Getting vdb paths from config file
        if "prop_vdb" in self.config.sections():
            self.prop_vdb = self.config.get("prop_vdb","prop_vdb_path",fallback=None)
            self.prop_vocab = self.config.get("prop_vdb", "prop_vocab_path", fallback=None)
        else:
            print("No Property vocabulary info found in the config file!")
        if "targ_vdb" in self.config.sections():
            self.targ_vdb = self.config.get("targ_vdb","targ_vdb_path", fallback=None)
            self.targ_vocab = self.config.get("targ_vdb", "targ_vocab_path", fallback=None)
        else:
            print("No Target vocabulary info found in the config file!")    
        if "duckling" in self.config.sections():
            self.duckling_url = self.config.get("duckling", "url", fallback=None)
        else:
            print("No Duckling URL in the config file! Temporal Expression Detection will not be working!")
        self.duckling_locale = self.config.get("duckling", "locale", fallback="en_CA")
        self.duckling_path = self.config.get("duckling", "path", fallback=None)
        self.duckling_run = self.duckling_path and os.path.isdir(self.duckling_path)
        if self.duckling_run:
            self.duckling_url = "http://0.0.0.0:8000/parse"
        self.duckling_dims = ["time"]

        # need either the vdb paths or the vocab paths to setup vdbs
        self.vdbs = Vdb_simsearch(self.prop_vdb, self.prop_vocab, self.targ_vdb, self.targ_vocab)
        # check if Duckling is running correctly
        self.duckling_parse("test - yesterday", dims=["time"])

    def duckling_parse(
        self,
        query: str,
        locale: Optional[str] = None,
        dims: Optional[List[str]] = None,
    ) -> Optional[JSON]:
        """Temporal Expression Detection using Duckling.
        Needs rasa/duckling Docker image running on duckling_url.
        Return a response json or None."""
        duckling_data = {
            "text": query,
            "locale": self.duckling_locale or locale,
        }
        if dims is None:
            dims = self.duckling_dims
        if dims:
            duckling_data["dims"] = json.dumps(dims)
        proc = None
        try:
            if self.duckling_run:
                proc = subprocess.Popen(
                    ["stack", "exec", "duckling-example-exe"],
                    cwd=self.duckling_path,
                    creationflags=(
                        subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
                        if sys.platform == "win32"
                        else 0
                    ),
                )
            for _ in range(5):
                try:
                    response = requests.post(self.duckling_url, data=duckling_data, timeout=1)
                except requests.exceptions.ConnectionError:
                    time.sleep(0.25)
                    continue
                if response.status_code == 200:
                    data = response.json()
                    if len(data) > 0:
                        return data[0]
                    else:
                        return None  # empty response
            else:
                raise Exception(f"Please make sure Duckling service is running on [{self.duckling_url}]!")
        except Exception as exc:
            raise Exception(f"Please make sure Duckling service is running on [{self.duckling_url}]!") from exc
        finally:
            if proc:
                proc.kill()

    def create_temporal_annotation(self, annotation) -> TemporalAnnotation:
        # get standard dateformat from text
        values = annotation['value']['values'][0]
        today = (datetime.datetime.today().date())
        tmrow = today + datetime.timedelta(days=1)
        # print(annotation)
        # #+/-infinity or #currentdate
        # TODO! cannot do yet operations like #currentdate-10Y
        start = "#-infinity"
        end = "#+infinity"
        if values['type'] == 'interval':
            if 'from' in values.keys():
                start = values['from']['value'][:19] + "Z"
                grain = values['from']['grain']
                if start[:10] == today.strftime("%Y-%m-%d"):
                    start = "#currentdate"
            if 'to' in values.keys():
                end = values['to']['value'][:19] + "Z"
                grain = values['to']['grain']
                # the end of today is tomorrow 00:00
                if end[:10] == today.strftime("%Y-%m-%d") or end[:10] == tmrow.strftime("%Y-%m-%d"):
                    end = "#currentdate"
        else:
            # one value, not interval
            val = values['value']
            grain = values['grain']
            if val[:10] == today.strftime("%Y-%m-%d") or val[:10] == tmrow.strftime("%Y-%m-%d"):
                val = "#currentdate"
            start = val[:19] + "Z"
            end = val[:19] + "Z"
        # fix end date
        if not end.startswith("#") and start==end:
            if grain == 'day':
                end = end[:11] + "11:59:59Z"
            elif grain == 'month':
                end = end[:8] + "31T11:59:59Z"
            elif grain == 'year':
                end = end[:5] + "12-31T11:59:59Z"
        return TemporalAnnotation(text=annotation['body'],  position=[annotation['start'], annotation['end']],
                                tempex_type="range", target="dataDate", value={'start':start,'end':end})


    def temporal_annotate(self, newq:str, nlq:str, verbose:bool=False):
        annotations = []
        duckling_annotation = self.duckling_parse(newq)
        if duckling_annotation:
            tempex = self.create_temporal_annotation(duckling_annotation)
            annotations.append(tempex)
            # remove temporal annotation span from query
            newq = newq[:tempex.position[0]] + newq[tempex.position[1]:]
            newq = newq.replace("  ", " ")
            if verbose:
                print("TEMPEX - V2:\n", tempex)
                print("New query:", newq)
        # tweak for years non-detected
        search_years = re.findall(r'\d{4}', newq)
        for year in search_years:
            year_annotation = self.duckling_parse("in " + year)
            if year_annotation:
                span, pos = find_spans(year, nlq)
                tempex = self.create_temporal_annotation({'body':span, 
                                                        'value':year_annotation['value'], 
                                                        'start':pos[0], 'end':pos[1]})
                annotations.append(tempex)
                # remove temporal annotation span from query
                newq = newq[:tempex.position[0]] + newq[tempex.position[1]:]
                newq = newq.replace("  ", " ")
                if verbose:
                    print("TEMPEX - V2:\n", tempex)
                    print("New query:", newq)
        return annotations, newq 
        
        
    def create_location_annotation(self, annotation) -> LocationAnnotation:
        # get geojson of location
        token, pos, gdf = annotation
        # have bbox coordinates if needed
        bbox = [gdf['bbox_north'].iloc[0], gdf['bbox_south'].iloc[0], 
                gdf['bbox_east'].iloc[0], gdf['bbox_west'].iloc[0]]
        return LocationAnnotation(text=token, position=pos,
                                  matching_type="overlap", name=gdf['display_name'].iloc[0], 
                                  value={"type": "Polygon", "coordinates": bbox})


    def create_property_annotation(self, annotation) -> PropertyAnnotation:
        # take annotation given by the engine
        # and create appropriate typeddict annotation
        # filling in each slot as required
        spans, poss, results = annotation
        prop_val, score = results
        prop_val = prop_val.split("::")
        val_type = 'string'  
        if len(prop_val) == 2:
            val = prop_val[1]
            if val.isnumeric():
                val_type = 'numeric'
        return PropertyAnnotation(text=spans, position=poss,
                                name=prop_val[0], value=prop_val[1], 
                                value_type=val_type, operation="eq")


    def create_target_annotation(self, annotation) -> TargetAnnotation:
        # get vdb simsearch results and fill annotation
        spans, poss, results = annotation
        varnames = []
        for res in results:
            if ", " in res:
                res_split = res.split(", ")
                for rs in res_split:
                    varnames.append(rs)
            else:
                varnames.append(res)
        return TargetAnnotation(text=spans,  position=poss, name=varnames)
        

    def transform_nl2query(self, nlq: str, verbose: bool = False) -> QueryAnnotationsDict:
        newq = nlq
        # collect annotations
        combined_annotations = []

        # temporal annotation
        tempex, newq = self.temporal_annotate(newq, nlq, verbose)
        combined_annotations+=(tempex)              
        
        # remove stopwords
        newq = remove_stopwords(newq)
        if verbose:
            print("Removing stopwords")
            print("New query:", newq) 
        
        # location annotation
        loc_span, osmnx_annotation = osmnx_geocode(self.vdbs, newq)
        if loc_span != None:
            _, pos = find_spans(loc_span, nlq)
            loc = self.create_location_annotation([loc_span, pos, osmnx_annotation])
            combined_annotations.append(loc)
            # remove loc annotations from newq
            _, newpos = find_spans(loc_span, newq)
            newq = newq[:newpos[0]] + newq[newpos[1]:]
            newq = newq.replace("   ", " ")
            newq = newq.replace("  ", " ")
            if verbose:
                print("LOCATION - V2:\n", loc)
                print("New query:", newq)
        
        
        # target annotation
        targ_span, targ_results = self.vdbs.query_ngram_target(newq, threshold=0.7)
        if len(targ_span) > 1 :
            targ_spans, pos = find_spans(targ_span, nlq)
            targ_annotation = self.create_target_annotation([targ_spans, pos, targ_results])
            combined_annotations.append(targ_annotation)
            # remove target annotations from newq
            _, newpos = find_spans(targ_span, newq)
            newq = newq[:newpos[0]] + newq[newpos[1]:]
            newq = newq.replace("   ", " ")
            newq = newq.replace("  ", " ")
            if verbose:
                print("TARGET - V2:\n", targ_annotation)
                print("New query:", newq)
        
        # property annotation
        prop_span, prop_results = self.vdbs.query_ngram_prop(newq, threshold=0.7)
        if len(prop_span) > 1:
            prop_spans, pos = find_spans(prop_span, nlq)
            prop_annotation = self.create_property_annotation([prop_spans, pos, prop_results])
            combined_annotations.append(prop_annotation)
            if verbose:
                print("PROPERTY - V2:\n", prop_annotation)
        
        # sort and return
        if len(combined_annotations) >1:
            combined_annotations.sort(key=lambda a:(a.position[0][0] 
                                  if isinstance(a.position[0], list) else a.position[0]))
        return QueryAnnotationsDict(query=nlq, annotations=combined_annotations)


    def run_ceda_queries(self, write_out:bool=False):
        """run V2 instance on ceda evaluation dataset"""
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
                    res = self.transform_nl2query(q['query'])
                    # print(res)
                    struct_results.append(res.to_dict())
            if write_out:
                ofile = path + "v2_ceda_test_results.json"
                with open(ofile, 'w', encoding="utf-8") as f:
                    json.dump({'queries': struct_results}, f, indent=2)
        return struct_results


if __name__ == "__main__":
    config_file = "v2_config.cfg"
    # call my nl2query class
    my_instance = V2_pipeline(config_file)
    # get the structured query from the nl query
    # query = "Downward UV radiation in uk from today to 2100"
    query = "uk climate ground wind strength and direction historical records"
    # query = "cmip6 greenhouse gas emission"
    structq = my_instance.transform_nl2query(query)
    print("\nStructured query: \n", structq)
    
    my_instance.run_ceda_queries(write_out=True)
