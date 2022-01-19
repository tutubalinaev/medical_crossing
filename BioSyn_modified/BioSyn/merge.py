import os
import glob
import argparse
import re
import requests
import lxml.html as lh
from lxml.html import fromstring
import json


def parse_args():
    parser = argparse.ArgumentParser()

    # Required
    parser.add_argument('--input_dict', type=str, required=True,
    help='path to target dict')
    parser.add_argument('--input_fre_dict', type=str, required=True,
    help='path to french dict')
    parser.add_argument('--output_dir', type=str, required=True,
    help='path to output directory')  
    args = parser.parse_args()
    return args

def main(args):
    input_dict = args.input_dict
    input_fre_dict = args.input_fre_dict
    output_dir = args.output_dir

    input_dict_mentions = []
    with open(args.input_dict,'r') as f:
        input_dict_mentions = f.readlines()
    with open(args.input_fre_dict,'r') as f:
        input_dict_mentions += f.readlines()
    for i,mention in enumerate(input_dict_mentions):
        input_dict_mentions[i] = mention.strip()         
    with open(output_dir + '{}'.format('/') + 'fr_merged_train_dictionary.txt','w') as g:
        for i,mention in enumerate(input_dict_mentions):
            if i != (len(input_dict_mentions) - 1):
                g.write(mention + '\n')
            else:
                g.write(mention)

if __name__ == '__main__':
  args = parse_args()
  main(args)