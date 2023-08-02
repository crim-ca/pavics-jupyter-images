import osmnx as ox
import requests
from nlp.notebooks.nl2query.NL2QueryInterface import *
import Vdb_simsearch


class V2_pipeline(NL2QueryInterface):

    def __init__(self, config:str=None):
        super().__init__(config)


    def create_temporal_annotation(self, annotation) -> TemporalAnnotation:
        # get standard dateformat from text
        values = annotation['value']['values'][0]
        if values['type'] == 'interval':
            return TemporalAnnotation(text=annotation['body'],  position=[annotation['start'], annotation['end']],
                                  tempex_type="range", target="dataDate", value={'start':values['from']['value'],
                                                                                 'end':values['to']['value']})
        else:
            return TemporalAnnotation(text=annotation['body'],  position=[annotation['start'], annotation['end']],
                                  tempex_type="point", target="dataDate", value=values)
        


    def create_location_annotation(self, annotation) -> LocationAnnotation:
        # get gejson of location
        token, gdf, query = annotation
        start_pos = query.index(token)
        bbox = [gdf['bbox_north'].iloc[0], gdf['bbox_south'].iloc[0], 
                gdf['bbox_east'].iloc[0], gdf['bbox_west'].iloc[0]]
        return LocationAnnotation(text=token, position=[start_pos, start_pos+len(token)],
                                  matching_type="overlap", name=gdf['display_name'].iloc[0], value={})


    def create_property_annotation(self, annotation) -> PropertyAnnotation:
        # take annotation given by the engine
        # and create appropriate typeddict annotation
        # filling in each slot as required
        span, results, orig_query = annotation
        print(results)
        prop_val, score = results
        prop_val = prop_val.split("::")
        start = orig_query.index(span)
        end = start + len(span)
        val_type = "string"
        if len(prop_val) == 2:
            val = prop_val[1]
            if val.isnumeric():
                val_type = 'numeric'
        return PropertyAnnotation(text=span, position=[start, end],
                                  name=prop_val[0], value=prop_val[1], 
                                  value_type=val_type, operation="eq")


    def create_target_annotation(self, annotation) -> TargetAnnotation:
        # get vdb simsearch results and fill annotation
        span, res, orig_query = annotation
        start = orig_query.index(span)
        end = start + len(span)
        return TargetAnnotation(text=span,  position=[start, end],
                                name=res)
         
    
    def duckling_parse(self, query):
        """Temporal Expression Detection
        using Duckling ran as a Docker
        must be run with -p 8000:8000"""
        url = " "
        duckling_data= {"text": query,
                        "locale": "en_GB",
                        "dims": "[\"time\"]"}
        try:
            response = requests.post('http://0.0.0.0:8000/parse', data=duckling_data)
            if response.status_code == 200:
                return response.json()[0]
        except:
            pass
        return None
   

    def osmnx_geocode(self, query:str):
        """location geocoding service
        queries every 1 and 2-gram tokens
        and return highest score result"""
        query_tokens,_ = Vdb_simsearch.generate_ngrams(query, 2)
        # query by 1-gram and 2-gram tokens
        importance = 0
        max_gdf = None
        max_token = None
        for token in query_tokens:
            try:
                gdf = ox.geocode_to_gdf(token)
                if len(gdf) > 0 and gdf['class'].iloc[0]in ['boundary', 'city', 'country', 'place']:
                    if gdf['importance'].iloc[0] > importance:
                        importance = gdf['importance'][0]
                        max_token = token
                        max_gdf = gdf
                # return token, gdf
            except:
                continue
        return (max_token, max_gdf)

    def transform_nl2query(self, nlq: str) -> QueryAnnotationsDict:
        newq = nlq
        # collect annotations
        combined_annotations = []

        # temporal annotation
        duckling_annotation = self.duckling_parse(newq)
        if duckling_annotation:
            tempex = self.create_temporal_annotation(duckling_annotation)
            combined_annotations.append(tempex)
            # remove temporal annotation span from query
            newq = newq.replace(duckling_annotation['body'] + " ", "")
            print("TEMPEX Result: ", tempex)
        print("\nNew query:", newq)
        
        # location annotation
        token, osmnx_annotation = self.osmnx_geocode(newq)
        if token:
            loc = self.create_location_annotation([token, osmnx_annotation, nlq])
            combined_annotations.append(loc)
            newq = newq.replace(token + " ", "")
            print("LOC Result:", loc)
        print("\nNew query:", newq)
        
        # property annotation
        prop_span, prop_results = Vdb_simsearch.query_ngram_prop(newq)
        prop_annotation = self.create_property_annotation([prop_span, prop_results, nlq])
        combined_annotations.append(prop_annotation)
        print("PROP Result:", prop_annotation)
        #TODO : remove or not the top prop annotation from query?
        
        # target annotation
        targ_span, targ_results = Vdb_simsearch.query_ngram_target(newq)
        targ_annotation = self.create_target_annotation([targ_span, targ_results, nlq])
        combined_annotations.append(targ_annotation)
        print("\nTARGET Result:", targ_annotation)
        
        # sort and return
        combined_annotations.sort(key=lambda a:a.position[0])
        return QueryAnnotationsDict(query=nlq, annotations=combined_annotations)


if __name__ == "__main__":
    query = "Sentinel-2 over Ottawa from april to september 2020 with cloud cover lower than 10%"
    config_file = "v2_config.cfg"
    # call my nl2query class
    my_instance = V2_pipeline(None)
    # get the structured query from the nl query
    structq = my_instance.transform_nl2query(query)
    print("Structured query: ", structq)

    # qfile = "ceda_gold_queries.json"
    # ofile = "ceda_test_results.json"
    # struct_results = []
    # with open(qfile, 'r') as f:
    #     qs = json.load(f)
    #     if 'queries' in qs.keys():
    #         qlist = qs['queries']
    #         # iterate over queries
    #         for q in qlist:
    #             print(q)
    #             res = my_instance.transform_nl2query(q['query'])
    #             print(res)
    #             struct_results.append(res.to_dict())
    #     print(struct_results)
    #     with open(ofile, 'w') as f:
    #         json.dump({'queries': struct_results}, f)




