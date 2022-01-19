import numpy as np
import torch
import argparse
import logging
import time
import pdb
import os
import json
import random
import scipy
import faiss

from utils import (
    evaluate
)
from math import ceil

from tqdm import tqdm
from src.biosyn import (
    QueryDataset, 
    CandidateDataset, 
    DictionaryDataset,
    TextPreprocess, 
    RerankNet, 
    BioSyn
)
from init_logging import init_logging

LOGGER = logging.getLogger()

def parse_args():
    """
    Parse input arguments
    """
    parser = argparse.ArgumentParser(description='Biosyn train')

    # Required
    parser.add_argument('--model', required=True,
                        help='Name of the model (from HuggingFace repo) or path')
    parser.add_argument('--train_dictionary_path', type=str, required=True,
                    help='train dictionary path')
    parser.add_argument('--train_dir', type=str, required=True,
                    help='training set directory')
    parser.add_argument('--output_dir', type=str, required=True,
                        help='Directory for output')
    
    # Tokenizer settings
    parser.add_argument('--max_length', default=25, type=int)

    # Train config
    parser.add_argument('--block_size',  type=int, 
                        default=50000)
    parser.add_argument('--seed',  type=int, 
                        default=0)
    parser.add_argument('--use_cuda',  action="store_true")
    parser.add_argument("--use_context", action="store_true")
    parser.add_argument('--topk',  type=int, 
                        default=20)
    parser.add_argument('--learning_rate',
                        help='learning rate',
                        default=0.0001, type=float)
    parser.add_argument('--weight_decay',
                        help='weight decay',
                        default=0.01, type=float)
    parser.add_argument('--train_batch_size',
                        help='train batch size',
                        default=16, type=int)
    parser.add_argument('--epoch',
                        help='epoch to train',
                        default=10, type=int)
    parser.add_argument('--initial_sparse_weight',
                        default=0, type=float)
    parser.add_argument('--dense_ratio', type=float,
                        default=0.5)
    parser.add_argument('--freeze_layers', type=int,
                        default=0, help='Number of starting layers to freeze during training in dense encoder')
    parser.add_argument('--freeze_embeddings',  action="store_true",
                        help='Freeze all embeddings (including word_embeddings) layers during training in dense encoder')
    parser.add_argument('--freeze_word_embeddings',  action="store_true",
                        help='Freeze word_embeddings layer during training in dense encoder')
    parser.add_argument('--save_checkpoint_all', action="store_true")

    args = parser.parse_args()
    return args


# def init_logging(output_dir):
#     LOGGER.setLevel(logging.INFO)
    
#     fmt = logging.Formatter('%(asctime)s: [ %(message)s ]',
#                             '%m/%d/%Y %I:%M:%S %p')
    
#     console = logging.StreamHandler()
#     console.setFormatter(fmt)
#     LOGGER.addHandler(console)
    
#     fileHandler = logging.FileHandler(f"{output_dir}/training.log")
#     fileHandler.setFormatter(fmt)
#     LOGGER.addHandler(fileHandler)
    

def init_seed(seed=None):
    if seed is None:
        seed = int(round(time.time() * 1000)) % 10000

    LOGGER.info("Using seed={}, pid={}".format(seed, os.getpid()))
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    random.seed(seed)
    torch.backends.cudnn.deterministic = True
    
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
    
def load_queries(data_dir, filter_composite, filter_duplicate, use_context):
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
        filter_duplicate=filter_duplicate,
        use_context=use_context
    )
    
    return dataset.data

def train(args, data_loader, model):
    LOGGER.info("train!")
    
    train_loss = 0
    train_steps = 0
    model.train()
    for i, data in tqdm(enumerate(data_loader), total=len(data_loader)):
        model.optimizer.zero_grad()
        batch_x, batch_y = data
        batch_pred = model(batch_x)  
        loss = model.get_loss(batch_pred, batch_y)
        loss.backward()
        model.optimizer.step()
        train_loss += loss.item()
        train_steps += 1

    train_loss /= (train_steps + 1e-9)
    return train_loss
    
def main(args):
    init_seed(args.seed)
    print(args)
    
    # prepare for output
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
        
    init_logging(args.output_dir, 'train', LOGGER)
        
    # load dictionary and queries
    train_dictionary = load_dictionary(dictionary_path=args.train_dictionary_path)
    train_queries = load_queries(
        data_dir = args.train_dir, 
        filter_composite=True,
        filter_duplicate=True,
        use_context=args.use_context
    )
        
    # filter only names
    names_in_train_dictionary = train_dictionary[:,0]
    names_in_train_queries = train_queries[:,0]

    # load BERT tokenizer, dense_encoder, sparse_encoder
    biosyn = BioSyn()
    encoder, tokenizer = biosyn.init_automodel(
        name=args.model,
        max_length=args.max_length,
        use_cuda=args.use_cuda,
        freeze_layer_count=args.freeze_layers,
        freeze_embeddings=args.freeze_embeddings,
        freeze_word_embeddings=args.freeze_word_embeddings,
    )
    sparse_encoder = biosyn.train_sparse_encoder(corpus=names_in_train_dictionary)
    sparse_weight = biosyn.init_sparse_weight(
        initial_sparse_weight=args.initial_sparse_weight,
        use_cuda=args.use_cuda
    )
    
    # load rerank model
    model = RerankNet(
        encoder = encoder,
        learning_rate=args.learning_rate, 
        weight_decay=args.weight_decay,
        sparse_weight=sparse_weight,
        use_cuda=args.use_cuda
    )
    
    # embed sparse representations for query and dictionary
    # Important! This is one time process because sparse represenation never changes.
    train_sparse_score_matrix = []
    train_sparse_candidate_idxs = []
    LOGGER.info("Sparse embedding")
    train_query_sparse_embeds = biosyn.embed_sparse(names=names_in_train_queries) # scipy.sparse.csr_matrix(biosyn.embed_sparse(names=names_in_train_queries))
    train_dict_sparse_embeds = biosyn.embed_sparse(names=names_in_train_dictionary) # scipy.sparse.csr_matrix(biosyn.embed_sparse(names=names_in_train_dictionary))
    """ train_sparse_candidate_idxs = biosyn.get_candidates(train_query_sparse_embeds, 
                                                        train_dict_sparse_embeds.T, 
                                                        ceil(train_dict_sparse_embeds.T.shape[1] / 100), 
                                                        args.topk) """
    LOGGER.info("Constructing score matrix")
    index = faiss.IndexFlatIP(train_dict_sparse_embeds.shape[1])
    index.add(train_dict_sparse_embeds)
    #train_sparse_score_matrix = biosyn.get_score_matrix(
    #    query_embeds=train_query_sparse_embeds, 
    #    dict_embeds=train_dict_sparse_embeds
    #)
    #LOGGER.info("Retrieving candidates")
    #train_sparse_candidate_idxs = biosyn.retrieve_candidate(
    #    score_matrix=train_sparse_score_matrix, 
    #    topk=args.topk
    #)
    LOGGER.info("Retrieving candidates")
    _, train_sparse_candidate_idxs = index.search(train_query_sparse_embeds, args.topk)
    train_sparse_candidate_idxs = train_sparse_candidate_idxs.astype(np.int32)
    #print(type(train_sparse_candidate_idxs[0][0]))
    #exit()
    # prepare for data loader of train and dev
    index = None
    train_set = CandidateDataset(
        queries = train_queries, 
        dicts = train_dictionary, 
        tokenizer = tokenizer, 
        topk = args.topk, 
        d_ratio=args.dense_ratio,
        #s_score_matrix=index, #train_sparse_score_matrix,
        dict_sparse_embeds=train_dict_sparse_embeds,
        query_sparse_embeds=train_query_sparse_embeds,
        s_candidate_idxs=train_sparse_candidate_idxs,
        max_length=args.max_length,
    )
    train_loader = torch.utils.data.DataLoader(
        train_set,
        batch_size=args.train_batch_size,
        shuffle=True,
    )

    start = time.time()
    for epoch in range(1,args.epoch+1):
        # embed dense representations for query and dictionary for train
        # Important! This is iterative process because dense represenation changes as model is trained.
        LOGGER.info("Epoch {}/{}".format(epoch,args.epoch))
        LOGGER.info("QUERIES train_set dense embedding for iterative candidate retrieval")
        train_query_dense_embeds = biosyn.embed_dense(names=list(names_in_train_queries), show_progress=True)
        LOGGER.info("DICTIONARY train_set dense embedding for iterative candidate retrieval")
        train_dict_dense_embeds = biosyn.embed_dense(names=list(names_in_train_dictionary), show_progress=True)
        #train_query_dense_embeds = np.random.rand(2000, 768)
        #train_dict_dense_embeds = np.random.rand(71924  , 768)
        LOGGER.info("GETTING CANDIDATES train_set dense embedding for iterative candidate retrieval")
        train_dense_candidate_idxs = biosyn.get_candidates(train_query_dense_embeds, 
                                                            train_dict_dense_embeds.T, 
                                                            args.block_size, 
                                                            args.topk)
        """ train_dense_score_matrix = biosyn.get_score_matrix(
            query_embeds=train_query_dense_embeds, 
            dict_embeds=train_dict_dense_embeds
        )
        train_dense_candidate_idxs = biosyn.retrieve_candidate(
            score_matrix=train_dense_score_matrix, 
            topk=args.topk
        ) """
        # replace dense candidates in the train_set
        train_set.set_dense_candidate_idxs(d_candidate_idxs=train_dense_candidate_idxs)

        # train
        train_loss = train(args, data_loader=train_loader, model=model)
        LOGGER.info('loss/train_per_epoch={}/{}'.format(train_loss,epoch))
        
        # save model every epoch
        if args.save_checkpoint_all:
            checkpoint_dir = os.path.join(args.output_dir, "checkpoint_{}".format(epoch))
            if not os.path.exists(checkpoint_dir):
                os.makedirs(checkpoint_dir)
            biosyn.save_model(checkpoint_dir)
        
        # save model last epoch
        if epoch == args.epoch:
            biosyn.save_model(args.output_dir)
            
    end = time.time()
    training_time = end-start
    training_hour = int(training_time/60/60)
    training_minute = int(training_time/60 % 60)
    training_second = int(training_time % 60)
    LOGGER.info("Training Time!{} hours {} minutes {} seconds".format(training_hour, training_minute, training_second))
    
if __name__ == '__main__':
    args = parse_args()
    main(args)
