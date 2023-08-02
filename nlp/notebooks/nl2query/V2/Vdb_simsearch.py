import os
# from langchain.llms import OpenLLM
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate

VDB_PATH = "/misc/data23-bs/DACCS/wp15/nlu_v2/"
VOC_PATH = "/media/sf_wp15/nlu_v2/"
VDB_PATH = "/home/vboxuser/Projects/"
os.environ['TRANSFORMERS_CACHE'] = VDB_PATH + 'llm/'
PROP_VDB_PATH = VDB_PATH + "chroma_vdb/prop_vdb"
TARG_VDB_PATH = VDB_PATH + "chroma_vdb/target_vdb"

llm = None
# OpenLLM(
#     model_name='flan-t5',
#     model_id='google/flan-t5-large',
# )

embeddings = HuggingFaceEmbeddings(
    model_name='intfloat/e5-base-v2',
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': False}
)

text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)

def get_vdb(db_dir, texts, embeddings):
    if os.path.exists(db_dir):
        print("Loading Chroma Vdb...")
        return Chroma(persist_directory=db_dir, embedding_function=embeddings)
    else:
        print("Creating Chroma Vdb...")
        db = Chroma.from_documents(texts, embedding=embeddings, persist_directory=db_dir)
        # Save vector database as persistent files in the output folder
        db.persist()
        return db
    
    
def get_prop_db(vdb_dir):
    # load csv
    loader = CSVLoader(file_path=VOC_PATH + 'prop_vocab.csv', csv_args={
        'delimiter': '#',
        'quotechar': '"',
        'fieldnames': ['propval', 'description']}, 
        source_column="propval") #specify a source for the document created from each row. Otherwise file_path will be used as the source for all documents created from the CSV file.
    documents = loader.load()
    texts = text_splitter.split_documents(documents)
    db = get_vdb(vdb_dir, texts, embeddings)
    return db
    
    
prop_db = get_prop_db(PROP_VDB_PATH)


def query_prop_qa(query):
    # Run similarity search query
    relevant = prop_db.similarity_search(query, k=10, include_metadata=True)
    # Define the prompt template
    reg_prompt = PromptTemplate(template="Given the context: {context}\n,\
                List the propvals corresponding to each term from the expression: {question}",
                                   input_variables=["context", "question"])

    # Define the question-answering chain =
    qa_chain = load_qa_chain(llm, chain_type="stuff", prompt=reg_prompt)
    res = qa_chain({"input_documents": relevant, "question": query})
    for t in res['input_documents']:
        print(t.page_content.split("\n")[0][9:])
#     print(res['output_text'])
    return res['output_text']
    
    
def get_target_db(vdb_dir):
    # load csv
    loader = CSVLoader(file_path= VOC_PATH + 'target_vocab2.csv', csv_args={
            'delimiter': '#',
            'quotechar': '"',
            'fieldnames': ['varname', 'description']}, 
            source_column="varname") #specify a source for the document created from each row. Otherwise file_path will be used as the source for all documents created from the CSV file.
    documents = loader.load()
    texts = text_splitter.split_documents(documents)
    db = get_vdb(vdb_dir, texts, embeddings)
    return db
    
    
targ_db = get_target_db(TARG_VDB_PATH)

def query_target_qa(query):
    # Run similarity search query
    relevant = targ_db.similarity_search(query, k=10, include_metadata=True)
    # Define the prompt template
    reg_prompt = PromptTemplate(template="Given the context: {context}\n,\
                List the varnames corresponding to each term from the expression: {question}",
                                   input_variables=["context", "question"])

    # Define the question-answering chain =
    qa_chain = load_qa_chain(llm, chain_type="stuff", prompt=reg_prompt)
    res = qa_chain({"input_documents": relevant, "question": query})
    for t in res['input_documents']:
        print(t.page_content.split("\n")[0][9:])
#     print(res['output_text'])
    return res['output_text']

def generate_ngrams(text, max_words):
    words = text.split()
    output = [] 
    ngrams_dict = {}
    for x in range(1,max_words+1):
        for i in range(len(words)- x+1):
            ngram = " ".join(words[i:i+x])
            output.append(ngram)
            # add 1-grams
            ngrams_dict[ngram] = words[i:i+x]
            # add 2-grams in case of 3-gram and more
            if x-i >= 2:
                for j in range(0, len(ngrams_dict[ngram])-1):
                    ngrams_dict[ngram].append(" ".join(words[i+j:i+j+2]))
    return output, ngrams_dict


def query_one_target(query, k=20, score_t=0.5, verbose=False):
    relevant = targ_db.similarity_search_with_relevance_scores(query, k=k, 
                                                                  include_metadata=True, 
                                                                  score_threshold=score_t)
    rel_docs = []
    scores = []
    if verbose:
        print("\nQUERY: ", query)
        print("RESULTS: ", len(relevant))
    for (t,score) in relevant:
        v = t.page_content.split("\n")[0]
        if v.startswith("varname: "):
            v = v[9:]
        if verbose:
            print(v, score)
        rel_docs.append(v)#(v, score))
        scores.append(score)
    return rel_docs, scores


def query_ngram_target(query, ngrams=3, threshold=0.6, verbose=False):
    # generate ngrams up to length 3 by default
    ngrams_list, ngrams_dict = generate_ngrams(query, ngrams) 
    ngrams_list += [query]
    ngram_results = {}
    ngram_scores = {}
    for ngrams in ngrams_list:
        # remember which results come from which query to identify span
        ngram_results[ngrams], ngram_scores[ngrams] = query_one_target(ngrams, score_t=threshold, verbose=verbose)
            
    # join ngram results
    if verbose:
        print("\nJOINT RESULTS:")
    join_results = {}
    join_scores = {}
    top_score = 0
    top_span = ""
    max_len = 0
    max_span = ""
    
    for k,v in ngram_results.items():
        if verbose:
            print("")
            print(k, len(v))
        join_results[k] = v
        join_scores[k] = ngram_scores[k]
        if k!= query and " " in k: # not full query nor 1-gram
            for ngram in ngrams_dict[k]:
                if len(ngram_results[ngram]) > 0:
                    add_list = [r for r in ngram_results[ngram] if r not in join_results[k]]
                    join_results[k] += add_list
                    index_scores = [ngram_results[ngram].index(e) for e in add_list]
                    join_scores[k] += [ngram_scores[ngram][s] for s in index_scores]
                if verbose:
                    print(ngram, len(ngram_results[ngram]))
        if len(join_scores[k])>0:
            join_avg = sum(join_scores[k])/len(join_scores[k])
            if verbose:
                print("AVG :", join_avg)
            if join_avg > top_score:
                top_score = join_avg
                top_span = k
        if len(join_results[k]) > max_len:
            max_len = len(join_results[k])
            max_span = k
        if verbose:
            print("LEN :", len(join_results[k]))
    if verbose:
        print("\nBEST RESULT:")
        print("BY HIGHEST SCORE:")
        print(top_score, top_span, join_results[top_span]) 
        print("OR")
        print("BY HIGHEST LENGTH:")
        print(max_len, max_span, join_results[max_span])
    # return top results above a threshold
    return top_span, join_results[top_span]


def query_one_prop(query, k=5, score_t=0.5, verbose=False):
    if verbose:
        print("\nQUERY: ", query)
    relevant = prop_db.similarity_search_with_relevance_scores(query, k=k, 
                                                                  include_metadata=True, 
                                                                  score_threshold=score_t)
    rel_docs = []
    for (t,score) in relevant:
        v = t.page_content.split("\n")[0]
        if v.startswith("propval: "):
            v = v[9:]
        if verbose:
            print(v, score)
        rel_docs.append((v, score))
    return rel_docs


def query_ngram_prop(query, ngrams=3, threshold=0.6, verbose=False):
    collect_results = []
    # generate ngrams up to length 3
    ngrams_list, _ = generate_ngrams(query, ngrams)
    ngrams_list += [query]
    ngram_results = {}
    for ngrams in ngrams_list:
        rel_docs = query_one_prop(ngrams, score_t=threshold, verbose=verbose)
        # remember which results come from wihch query to identify span
        if len(rel_docs) > 0:
            ngram_results[ngrams] = rel_docs
            collect_results+=(rel_docs)
        else:
            ngram_results[ngrams] = []
            
    # sort results by descending score
    collect_results = sorted(collect_results, key= lambda x: x[1], reverse=True)
    
    top_res = {}
    if collect_results:
        # remove duplicates
        set_results = [collect_results[0]]
        for (t,score) in collect_results:
            if t not in list(zip(*set_results))[0]:
                set_results.append((t,score))
                
        # return highest score results
        for item in set_results:
            # find span (ngram) that resulted this
            for k,v in ngram_results.items():
                if item in v:
                    if k not in top_res.keys():
                        # take only highest score first item per span
                        top_res[k]= item
    if verbose:
        print("\nTOP RESULTS:", top_res)
    # return top result
    # TODO above a threshold or other condition
    return list(top_res.items())[0]

if __name__ == "__main__":
    
    query_one_prop("sentinel", verbose=True)
    # query_one_target("precipitation", verbose=True)

    # query = "sentinel daily rain amount"
    # query_ngram_prop(query, verbose=True)
    # query_ngram_target(query, verbose=True)