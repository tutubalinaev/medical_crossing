import argparse
import logging
import os
import json
from tqdm import tqdm
from utils import (
    evaluate
)
from src.biosyn import (
    DictionaryDataset,
    QueryDataset,
    BioSyn
)

from init_logging import init_logging

LOGGER = logging.getLogger()


def parse_args():
    """
    Parse input arguments
    """
    parser = argparse.ArgumentParser(description='BioSyn evaluation')

    # Required
    parser.add_argument('--model_dir', required=True, help='Directory for model')
    parser.add_argument('--dictionary_path', type=str, required=True, help='dictionary path')
    parser.add_argument('--data_dir', type=str, required=True, help='data set to evaluate')

    # Run settings
    parser.add_argument('--block_size',  type=int, default=50000)
    parser.add_argument('--use_cuda',  action="store_true")
    parser.add_argument("--use_context", action="store_true")
    parser.add_argument('--topk',  type=int, default=20)
    parser.add_argument('--score_mode',  type=str, default='hybrid', help='hybrid/dense/sparse')
    parser.add_argument('--output_dir', type=str, default='./output/', help='Directory for output')
    parser.add_argument('--filter_composite', action="store_true", help="filter out composite mention queries")
    parser.add_argument('--filter_duplicate', action="store_true", help="filter out duplicate queries")
    parser.add_argument('--save_predictions', action="store_true", help="whether to save predictions")

    # Tokenizer settings
    parser.add_argument('--max_length', default=25, type=int)
    
    args = parser.parse_args()
    return args
    
# def init_logging():
#     LOGGER.setLevel(logging.INFO)
#     fmt = logging.Formatter('%(asctime)s: [ %(message)s ]',
#                             '%m/%d/%Y %I:%M:%S %p')
#     console = logging.StreamHandler()
#     console.setFormatter(fmt)
#     LOGGER.addHandler(console)

def load_dictionary(dictionary_path): 
    dictionary = DictionaryDataset(
        dictionary_path = dictionary_path
    )
    return dictionary.data

def load_queries(data_dir, filter_composite, filter_duplicate, use_context):
    dataset = QueryDataset(
        data_dir=data_dir,
        filter_composite=filter_composite,
        filter_duplicate=filter_duplicate,
        use_context=use_context
    )
    return dataset.data
                
def main(args):
    #init_logging()
    print(args)
    
    init_logging(args.output_dir, 'eval', LOGGER)

    # load dictionary and data
    eval_dictionary = load_dictionary(dictionary_path=args.dictionary_path)
    eval_queries = load_queries(
        data_dir=args.data_dir,
        filter_composite=args.filter_composite,
        filter_duplicate=args.filter_duplicate,
        use_context=args.use_context
    )

    biosyn = BioSyn().load_model(
            path=args.model_dir,
            max_length=args.max_length,
            use_cuda=args.use_cuda
    )

    LOGGER.info(f"Sparse encoder vocab size: {len(biosyn.sparse_encoder.vocab())}")
    LOGGER.info(f"Encoding sparse features based on {args.dictionary_path}")
    # retraining on dictionary every time now!
    biosyn.sparse_encoder.fit([n for n, c in list(eval_dictionary)])
    LOGGER.info(f"Encoding sparse features done.")
    LOGGER.info(f"Sparse encoder vocab size, updated: {len(biosyn.sparse_encoder.vocab())}")
    LOGGER.info(f"Sparse encoder vocab: {biosyn.sparse_encoder.vocab()}")
    
    result_evalset = evaluate(
        biosyn=biosyn,
        eval_dictionary=eval_dictionary,
        eval_queries=eval_queries,
        topk=args.topk,
        score_mode=args.score_mode,
        block_size=args.block_size
    )
    
    LOGGER.info("acc@1={}".format(result_evalset['acc1']))
    LOGGER.info("acc@5={}".format(result_evalset['acc5']))
    
    if args.save_predictions:
        output_file = os.path.join(args.output_dir,"predictions_eval.json")
        with open(output_file, 'w') as f:
            json.dump(result_evalset, f, indent=2)

if __name__ == '__main__':
    args = parse_args()
    main(args)
