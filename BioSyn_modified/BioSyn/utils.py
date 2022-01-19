import csv
import json
import numpy as np
import pdb
from tqdm import tqdm
import faiss
from math import ceil

def check_k(queries):
    return len(queries[0]['mentions'][0]['candidates'])

def evaluate_topk_acc(data):
    """
    evaluate acc@1~acc@k
    """
    queries = data['queries']
    k = check_k(queries)

    for i in range(0, k):
        hit = 0
        for query in queries:
            mentions = query['mentions']
            mention_hit = 0
            for mention in mentions:
                candidates = mention['candidates'][:i+1] # to get acc@(i+1)
                mention_hit += np.any([candidate['label'] for candidate in candidates])
            
            # When all mentions in a query are predicted correctly,
            # we consider it as a hit 
            if mention_hit == len(mentions):
                hit +=1
        
        data['acc{}'.format(i+1)] = hit/len(queries)

    return data

def check_label(predicted_cui, golden_cui):
    """
    Some composite annotation didn't consider orders
    So, set label '1' if any cui is matched within composite cui (or single cui)
    Otherwise, set label '0'
    """
    return int(len(set(predicted_cui.split("|")).intersection(set(golden_cui.split("|"))))>0)

def predict_topk(biosyn, eval_dictionary, eval_queries, topk, score_mode='hybrid', block_size=50000):
    """
    Parameters
    ----------
    score_mode : str
        hybrid, dense, sparse
    """
    encoder = biosyn.get_dense_encoder()
    tokenizer = biosyn.get_dense_tokenizer()
    sparse_encoder = biosyn.get_sparse_encoder()
    sparse_weight = biosyn.get_sparse_weight().item() # must be scalar value
    
    # embed dictionary
    dict_sparse_embeds = biosyn.embed_sparse(names=eval_dictionary[:,0], show_progress=True)

    if score_mode == "hybrid" or score_mode == "dense":
        dict_dense_embeds = biosyn.embed_dense(names=list(eval_dictionary[:,0]), show_progress=True)
    
    queries = []

    for eval_query in tqdm(eval_queries, total=len(eval_queries)):

        mentions = eval_query[0].replace("+","|").split("|")
        golden_cui = eval_query[1].replace("+","|")
        dict_mentions = []

        for mention in mentions:

            mention_sparse_embeds = biosyn.embed_sparse(names=np.array([mention]))
            mention_dense_embeds = None

            if score_mode == "hybrid" or score_mode == "dense":
                mention_dense_embeds = biosyn.embed_dense(names=[mention])
            
            # get score matrix
            if score_mode == 'hybrid':
                candidate_idxs = biosyn.get_candidates_hybrid_inference(mentions_sparse=mention_sparse_embeds, 
                                                                        mentions_dense=mention_dense_embeds, 
                                                                        vocab_sparse=dict_sparse_embeds.T, 
                                                                        vocab_dense=dict_dense_embeds.T,
                                                                        sparse_weight=sparse_weight, 
                                                                        block_size=block_size, 
                                                                        n_top=topk)
            elif score_mode == 'dense':
                dense_score_matrix = biosyn.get_score_matrix(
                query_embeds=mention_dense_embeds, 
                dict_embeds=dict_dense_embeds
                )
                score_matrix = dense_score_matrix
                index = faiss.IndexFlatL2(dict_dense_embeds.shape[1])
                index.add(dict_dense_embeds)              
                k = 5                        
                D, I = index.search(mention_dense_embeds, k)
                candidate_idxs = I
            elif score_mode == 'sparse':
                index = faiss.IndexFlatL2(dict_sparse_embeds.shape[1])
                index.add(dict_sparse_embeds)              
                k = 5                        
                D, I = index.search(mention_sparse_embeds, k)
                candidate_idxs = I
            else:
                raise NotImplementedError()

            

            np_candidates = eval_dictionary[candidate_idxs].squeeze()
            dict_candidates = []
            for np_candidate in np_candidates:
                dict_candidates.append({
                    'name':np_candidate[0],
                    'cui':np_candidate[1],
                    'label':check_label(np_candidate[1],golden_cui)
                })
            dict_mentions.append({
                'mention':mention,
                'golden_cui':golden_cui, # golden_cui can be composite cui
                'candidates':dict_candidates
            })
        queries.append({
            'mentions':dict_mentions
        })
    
    result = {
        'queries':queries
    }

    return result

def evaluate(biosyn, eval_dictionary, eval_queries, topk, score_mode='hybrid', block_size=50000):
    """
    predict topk and evaluate accuracy
    
    Parameters
    ----------
    biosyn : BioSyn
        trained biosyn model
    eval_dictionary : str
        dictionary to evaluate
    eval_queries : str
        queries to evaluate
    topk : int
        the number of topk predictions
    score_mode : str
        hybrid, dense, sparse

    Returns
    -------
    result : dict
        accuracy and candidates
    """
    result = predict_topk(biosyn,eval_dictionary,eval_queries, topk, score_mode, block_size)
    result = evaluate_topk_acc(result)
    
    return result