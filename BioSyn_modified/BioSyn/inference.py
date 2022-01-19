import argparse
import os
import pdb
import pickle
import faiss
import json
from src.biosyn import (
    QueryDataset,
    DictionaryDataset,
    BioSyn,
    TextPreprocess
)
from utils import (
    predict_topk
)

def parse_args():
    """
    Parse input arguments
    """
    parser = argparse.ArgumentParser(description='BioSyn Demo')

    # Required
    parser.add_argument('--mention', type=str, help='mention to normalize')
    parser.add_argument('--output_dir', help='path to the output directory')
    parser.add_argument('--model_dir', help='Directory for model')
    parser.add_argument('--dictionary_path', type=str, required=True,
    help='dictionary path')
    parser.add_argument('--concepts_dir', type=str, required=True,
    help='path to directory with concepts')
    parser.add_argument('--max_length', default=25, type=int)
    # Settings
    parser.add_argument('--show_embeddings',  action="store_true")
    parser.add_argument('--show_predictions',  action="store_true")
    parser.add_argument('--show_baseline_json_with_predicts',  action="store_true")
    parser.add_argument('--use_cuda',  action="store_true")
    parser.add_argument('--initial_sparse_weight',
    default=0, type=float)
    args = parser.parse_args()
    return args

def cache_or_load_dictionary(biosyn, dictionary_path):
    dictionary_name = os.path.splitext(os.path.basename(args.dictionary_path))[0]

    cached_dictionary_path = os.path.join(
    './tmp',
    "cached_{}.pk".format(dictionary_name)
    )

    # If exist, load the cached dictionary
    if os.path.exists(cached_dictionary_path):
        with open(cached_dictionary_path, 'rb') as fin:
            cached_dictionary = pickle.load(fin)
            print("Loaded dictionary from cached file {}".format(cached_dictionary_path))

            dictionary, dict_sparse_embeds, dict_dense_embeds = (
            cached_dictionary['dictionary'],
            cached_dictionary['dict_sparse_embeds'],
            cached_dictionary['dict_dense_embeds'],
            )
    else:
        dictionary = DictionaryDataset(dictionary_path = dictionary_path).data
        dictionary_names = dictionary[:,0]
        dict_sparse_embeds = biosyn.embed_sparse(names=dictionary_names, show_progress=True)
        dict_dense_embeds = biosyn.embed_dense(names=dictionary_names, show_progress=True)
        cached_dictionary = {
        'dictionary': dictionary,
        'dict_sparse_embeds' : dict_sparse_embeds,
        'dict_dense_embeds' : dict_dense_embeds
        }

    if not os.path.exists('./tmp'):
        os.mkdir('./tmp')
        with open(cached_dictionary_path, 'wb') as fin:
            pickle.dump(cached_dictionary, fin)
            print("Saving dictionary into cached file {}".format(cached_dictionary_path))

    return dictionary, dict_sparse_embeds, dict_dense_embeds

def load_dictionary(dictionary_path):
    """
    load dictionary

    Parameters
    ----------
    dictionary_path : str
    a path of dictionary
    """
    dictionary = DictionaryDataset(
    dictionary_path = dictionary_path
    )

    return dictionary.data

def load_queries(data_dir, filter_composite, filter_duplicate):
    """
    load query data

    Parameters
    ----------
    is_train : bool
    train or dev
    filter_composite : bool
    filter composite mentions
    filter_duplicate : bool
    filter duplicate queries
    """
    dataset = QueryDataset(
    data_dir=data_dir,
    filter_composite=filter_composite,
    filter_duplicate=filter_duplicate
    )

    return dataset.data

def get_acc1(test_cui, dict_cui):
    if dict_cui == test_cui:
        return 1
    return 0

def get_acc5(test_cui, dict_cuis):
    for el in dict_cuis:
        if el == test_cui:
            return 1
    return 0

def main(args):
    # load biosyn model
    if args.show_baseline_json_with_predicts:
      biosyn = BioSyn()

      biosyn.load_bert(
      path=args.model_dir,
      max_length=args.max_length,
      use_cuda=args.use_cuda,
      )

      eval_dictionary = load_dictionary(dictionary_path=args.dictionary_path)
      eval_queries = load_queries(
        data_dir = args.concepts_dir,
        filter_composite=True,
        filter_duplicate=True
      )

      biosyn.train_sparse_encoder(corpus=eval_dictionary[:,0])
      biosyn.init_sparse_weight(
      initial_sparse_weight=args.initial_sparse_weight,
      use_cuda=args.use_cuda
      )

      hybrid_evalset = predict_topk(
        biosyn=biosyn,
        eval_dictionary=eval_dictionary,
        eval_queries=eval_queries,
        topk=5,
        score_mode="hybrid"
      )

      dense_evalset = predict_topk(
        biosyn=biosyn,
        eval_dictionary=eval_dictionary,
        eval_queries=eval_queries,
        topk=5,
        score_mode="dense"
      )

      sparse_evalset = predict_topk(
        biosyn=biosyn,
        eval_dictionary=eval_dictionary,
        eval_queries=eval_queries,
        topk=5,
        score_mode="sparse"
      )


      output = {
        'sparse evalset':sparse_evalset,
        'dense evalset':dense_evalset,
        'hybrid evalset':hybrid_evalset
      }
      output_file = os.path.join(args.output_dir,"predictions_eval.json")
      with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    if args.show_embeddings:
        output = {
        'mention': args.mention,
        'mention_sparse_embeds': mention_sparse_embeds.squeeze(0),
        'mention_dense_embeds': mention_dense_embeds.squeeze(0)
        }

    if args.show_predictions:
        if args.dictionary_path == None:
            print('insert the dictionary path')
            return

        # cache or load dictionary
        dictionary, dict_sparse_embeds, dict_dense_embeds = cache_or_load_dictionary(biosyn, args.dictionary_path)

        # calcuate score matrix and get top 5
        sparse_score_matrix = biosyn.get_score_matrix(
        query_embeds=mention_sparse_embeds,
        dict_embeds=dict_sparse_embeds
        )
        dense_score_matrix = biosyn.get_score_matrix(
        query_embeds=mention_dense_embeds,
        dict_embeds=dict_dense_embeds
        )
        sparse_weight = biosyn.get_sparse_weight().item()
        hybrid_score_matrix = sparse_weight * sparse_score_matrix + dense_score_matrix
        hybrid_candidate_idxs = biosyn.retrieve_candidate(
        score_matrix = hybrid_score_matrix,
        topk = 5
        )

        # get predictions from dictionary
        predictions = dictionary[hybrid_candidate_idxs].squeeze(0)
        output['predictions'] = []

        for prediction in predictions:
            predicted_name = prediction[0]
            predicted_id = prediction[1]
            output['predictions'].append({
            'name': predicted_name,
            'id': predicted_id
            })

    print(output)

if __name__ == '__main__':
    args = parse_args()
    main(args)
