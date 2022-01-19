import os
import pickle
import logging
import torch
import numpy as np
import time
from math import ceil
import scipy

from tqdm import tqdm
from torch import nn
from .sparse_encoder import SparseEncoder
from .rerankNet import RerankNet

from transformers import (
    AutoConfig,
    AutoTokenizer,
    AutoModel
)

LOGGER = logging.getLogger()


class BioSyn(object):
    """
    Wrapper class for dense encoder and sparse encoder
    """

    def __init__(self):
        self.tokenizer = None
        self.encoder = None
        self.sparse_encoder = None
        self.sparse_weight = None
        self.model_name = None
        self.tokenizer_max_length = None

    def init_sparse_weight(self, initial_sparse_weight, use_cuda):
        """
        Parameters
        ----------
        initial_sparse_weight : float
            initial sparse weight
        """
        if use_cuda:
            self.sparse_weight = nn.Parameter(torch.empty(1).cuda())
        else:
            self.sparse_weight = nn.Parameter(torch.empty(1))
        self.sparse_weight.data.fill_(initial_sparse_weight) # init sparse_weight

        return self.sparse_weight

    def train_sparse_encoder(self, corpus):
        self.sparse_encoder = SparseEncoder().fit(corpus)

        return self.sparse_encoder

    def get_dense_encoder(self):
        assert (self.encoder is not None)

        return self.encoder

    def get_dense_tokenizer(self):
        assert (self.tokenizer is not None)

        return self.tokenizer

    def get_sparse_encoder(self):
        assert (self.sparse_encoder is not None)
        
        return self.sparse_encoder

    def get_sparse_weight(self):
        assert (self.sparse_weight is not None)
        
        return self.sparse_weight

    def save_model(self, path):
        # save bert model, bert config
        self.encoder.save_pretrained(path)

        # save bert vocab
        self.tokenizer.save_pretrained(path)
        
        # save sparse encoder

        sparse_encoder_path = os.path.join(path,'sparse_encoder.pk')
        self.sparse_encoder.save_encoder(path=sparse_encoder_path)
        
        sparse_weight_file = os.path.join(path,'sparse_weight.pt')
        torch.save(self.sparse_weight, sparse_weight_file)
        logging.info("Sparse weight saved in {}".format(sparse_weight_file))

    def init_automodel(self, name, max_length, use_cuda, freeze_layer_count=0, freeze_embeddings=False, freeze_word_embeddings=False):
        self.model_name = name
        self.tokenizer_max_length = max_length
        self.tokenizer = AutoTokenizer.from_pretrained(name)
        self.encoder = AutoModel.from_pretrained(name)

        if freeze_word_embeddings:
            for param in self.encoder.embeddings.word_embeddings.parameters():
                param.requires_grad = False

        if freeze_embeddings:
            for param in self.encoder.embeddings.parameters():
                param.requires_grad = False

        for layer in self.encoder.encoder.layer[:freeze_layer_count]:
            for param in layer.parameters():
                param.requires_grad = False

        # print("#Trainable params: ", sum(p.numel() for p in self.encoder.parameters() if p.requires_grad))

        if use_cuda:
            self.encoder.to(torch.device("cuda"))

        return self.encoder, self.tokenizer

    def load_model(self, path, max_length=25, use_cuda=True):
        self.load_automodel(path, max_length, use_cuda)
        self.load_sparse_encoder(path)
        self.load_sparse_weight(path)

        return self

    def load_automodel(self, path, max_length, use_cuda):
        self.tokenizer_max_length = max_length
        self.tokenizer = AutoTokenizer.from_pretrained(path)
        self.encoder = AutoModel.from_pretrained(path)

        if use_cuda:
            self.encoder.to(torch.device("cuda"))

        return self.encoder, self.tokenizer

    def load_sparse_encoder(self, path):
        self.sparse_encoder = SparseEncoder().load_encoder(path=os.path.join(path,'sparse_encoder.pk'))

        return self.sparse_encoder

    def load_sparse_weight(self, path):
        sparse_weight_file = os.path.join(path, 'sparse_weight.pt')
        self.sparse_weight = torch.load(sparse_weight_file)

        return self.sparse_weight

    def get_score_matrix(self, query_embeds, dict_embeds, is_sparse=False):
        """
        Return score matrix

        Parameters
        ----------
        query_embeds : np.array
            2d numpy array of query embeddings
        dict_embeds : np.array
            2d numpy array of query embeddings

        Returns
        -------
        score_matrix : np.array
            2d numpy array of scores
        """
        if scipy.sparse.issparse(query_embeds):
            score_matrix = query_embeds.dot( dict_embeds.transpose() )
        else:
            score_matrix = np.matmul(query_embeds, dict_embeds.T)
        
        return score_matrix

    def retrieve_candidate(self, score_matrix, topk):
        """
        Return sorted topk idxes (descending order)

        Parameters
        ----------
        score_matrix : np.array
            2d numpy array of scores
        topk : int
            The number of candidates

        Returns
        -------
        topk_idxs : np.array
            2d numpy array of scores [# of query , # of dict]
        """
        
        def indexing_2d(arr, cols):
            rows = np.repeat(np.arange(0,cols.shape[0])[:, np.newaxis],cols.shape[1],axis=1)
            return arr[rows, cols]

        # get topk indexes without sorting
        #topk_idxs = np.argpartition(score_matrix,-topk)[:, -topk:]
        topk_idxs = np.empty((score_matrix.shape[0], topk),dtype=np.int64)
        for i in range(score_matrix.shape[0]):
            if scipy.sparse.issparse(score_matrix):
                topk_idxs[i] = np.argpartition(score_matrix[i,:].toarray().T.squeeze(),-topk)[-topk:]
            else:
                topk_idxs[i] = np.argpartition(score_matrix[i,:],-topk)[-topk:]
        # get topk indexes with sorting
        topk_score_matrix = indexing_2d(score_matrix, topk_idxs)#.toarray()
        if scipy.sparse.issparse(topk_score_matrix):
            topk_argidxs = np.argsort(-topk_score_matrix.todense())
        else:
            topk_argidxs = np.argsort(-topk_score_matrix)
        topk_idxs = indexing_2d(topk_idxs, topk_argidxs)

        return topk_idxs

    def embed_sparse(self, names, show_progress=False):
        """
        Embedding data into sparse representations

        Parameters
        ----------
        names : np.array
            An array of names

        Returns
        -------
        sparse_embeds : np.array
            A list of sparse embeddings
        """
        batch_size=1024
        sparse_embeds = []
        
        if show_progress:
            iterations = tqdm(range(0, len(names), batch_size))
        else:
            iterations = range(0, len(names), batch_size)
        
        for start in iterations:
            end = min(start + batch_size, len(names))
            batch = names[start:end]
            batch_sparse_embeds = self.sparse_encoder(batch)
            batch_sparse_embeds = batch_sparse_embeds.numpy()
            sparse_embeds.append(batch_sparse_embeds)
        sparse_embeds = np.concatenate(sparse_embeds, axis=0)

        return sparse_embeds

    def embed_dense(self, names, show_progress=False):
        """
        Embedding data into sparse representations

        Parameters
        ----------
        names : np.array
            An array of names

        Returns
        -------
        dense_embeds : list
            A list of dense embeddings
        """
        self.encoder.eval() # prevent dropout
        
        batch_size=1024
        dense_embeds = []

        with torch.no_grad():
            if show_progress:
                iterations = tqdm(range(0, len(names), batch_size), "dense-embedding")
            else:
                iterations = range(0, len(names), batch_size)
                
            for start in iterations:
                end = min(start + batch_size, len(names))
                batch = names[start:end]
                batch_tokenized_names = self.tokenizer(batch, return_tensors="pt", padding='max_length', truncation=True,
                                                       max_length=self.tokenizer_max_length).to(torch.device("cuda"))
                last_hidden_state, _ = self.encoder(**batch_tokenized_names)
                batch_dense_embeds = last_hidden_state[:, 0]  # CLS token representation
                batch_dense_embeds = batch_dense_embeds.cpu().detach().numpy()
                dense_embeds.append(batch_dense_embeds)
        dense_embeds = np.concatenate(dense_embeds, axis=0)
        
        return dense_embeds

    def get_candidates(self, mentions, vocab, block_size, n_top):
        def indexing_2d(arr, cols):
            rows = np.repeat(np.arange(0,cols.shape[0])[:, np.newaxis],cols.shape[1],axis=1)
            return arr[rows, cols]
        start = 0
        sorted_list = []
        sorted_list_args = []
        iterator_times = ceil(vocab.shape[1] / block_size) * block_size
        append_shape = iterator_times - vocab.shape[1]
        zero = np.zeros((vocab.shape[0], int(append_shape)), )
        aligment_vocab = np.append(vocab, zero, axis=1)
        for i in tqdm(range(int(aligment_vocab.shape[1] / block_size)), total=int(aligment_vocab.shape[1] / block_size)):
            sliced = np.copy(aligment_vocab[:,start: start + block_size])
            sliced = mentions.dot(sliced)
            sliced_argsorted = np.argpartition(sliced, sliced.shape[1]-n_top, axis=1)[:,-n_top:]
            sorted_list_args.append(sliced_argsorted + block_size*i)
            sor = np.take_along_axis(sliced, sliced_argsorted, axis=1)
            sorted_list.append(sor[:,-n_top:])
            start += block_size
            del sliced
        m = np.hstack(sorted_list,)
        n = np.hstack(sorted_list_args,)
        chosen = np.argpartition(m, m.shape[1]-n_top, axis=1)[:,-n_top:]
        topk_idxs = np.take_along_axis(n,chosen, axis=1)
        topk_score_matrix = indexing_2d(m, chosen)
        
        topk_argidxs = np.argsort(-topk_score_matrix, axis=1)
        topk_idxs = indexing_2d(topk_idxs, topk_argidxs)
        return topk_idxs#, topk_score_matrix

    def get_candidates_hybrid_inference(self, mentions_sparse, mentions_dense, 
                                        vocab_sparse, vocab_dense,
                                        sparse_weight, block_size, n_top):
        def indexing_2d(arr, cols):
            rows = np.repeat(np.arange(0,cols.shape[0])[:, np.newaxis],cols.shape[1],axis=1)
            return arr[rows, cols]
        assert(vocab_sparse.shape[1] == vocab_dense.shape[1])
        start = 0
        sorted_list = []
        sorted_list_args = []
        iterator_times = ceil(vocab_sparse.shape[1] / block_size) * block_size
        append_shape = iterator_times - vocab_sparse.shape[1]
        zero_sparse = np.zeros((vocab_sparse.shape[0], int(append_shape)), )
        zero_dense = np.zeros((vocab_dense.shape[0], int(append_shape)), )

        aligment_vocab_sparse = np.append(vocab_sparse, zero_sparse, axis=1)
        aligment_vocab_dense = np.append(vocab_dense, zero_dense, axis=1)

        for i in tqdm(range(int(aligment_vocab_sparse.shape[1] / block_size)), total=int(aligment_vocab_sparse.shape[1] / block_size)):
            sliced_sparse = np.copy(aligment_vocab_sparse[:,start: start + block_size])
            sliced_dense = np.copy(aligment_vocab_dense[:,start: start + block_size])
            #score_matrix = sparse_weight * sparse_score_matrix + dense_score_matrix
            sliced = sparse_weight * mentions_sparse.dot(sliced_sparse) +  mentions_dense.dot(sliced_dense)
            sliced_argsorted = np.argpartition(sliced, sliced.shape[1]-n_top, axis=1)[:,-n_top:]
            sorted_list_args.append(sliced_argsorted + block_size*i)
            sor = np.take_along_axis(sliced, sliced_argsorted, axis=1)
            sorted_list.append(sor[:,-n_top:])
            start += block_size
            del sliced
        m = np.hstack(sorted_list,)
        n = np.hstack(sorted_list_args,)
        chosen = np.argpartition(m, m.shape[1]-n_top, axis=1)[:,-n_top:]
        topk_idxs = np.take_along_axis(n,chosen, axis=1)
        topk_score_matrix = indexing_2d(m, chosen)

        topk_argidxs = np.argsort(-topk_score_matrix, axis=1)
        topk_idxs = indexing_2d(topk_idxs, topk_argidxs)
        return topk_idxs