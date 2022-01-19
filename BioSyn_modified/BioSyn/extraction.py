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
    parser.add_argument('--input_dir', type=str, required=True,
    help='input directory')
    parser.add_argument('--output_dir', type=str, required=True,
    help='output directory')
    parser.add_argument('--french_dict', type=str, required=True,
    help='path to dict with french concepts')
    parser.add_argument('--german_dict', type=str, required=True,
    help='path to dict with french concepts')
    parser.add_argument('--output_json', type=str, required=True,
    help='path to output json for relations')
    parser.add_argument('--input_dict', type=str, required=True,
    help='path to output json for relations')
    args = parser.parse_args()
    return args

class Authentication:

    #def __init__(self, username,password):
    def __init__(self, apikey):
        #self.username=username
        #self.password=password
        self.apikey=apikey
        self.service="http://umlsks.nlm.nih.gov"

    def gettgt(self):
        uri="https://utslogin.nlm.nih.gov"
        auth_endpoint = "/cas/v1/api-key"
        #params = {'username': self.username,'password': self.password}
        params = {'apikey': self.apikey}
        h = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain", "User-Agent":"python" }
        r = requests.post(uri+auth_endpoint,data=params,headers=h)
        response = fromstring(r.text)
        ## extract the entire URL needed from the HTML form (action attribute) returned - looks similar to https://utslogin.nlm.nih.gov/cas/v1/tickets/TGT-36471-aYqNLN2rFIJPXKzxwdTNC5ZT7z3B3cTAKfSc5ndHQcUxeaDOLN-cas
        ## we make a POST call to this URL in the getst method
        tgt = response.xpath('//form/@action')[0]
        return tgt

    def getst(self,tgt):

        params = {'service': self.service}
        h = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain", "User-Agent":"python" }
        r = requests.post(tgt,data=params,headers=h)
        st = r.text
        return st

def query_parse(text,input_type='query'):
    mentions = []
    if input_type == 'query':
        for line in text:
            mention = line.split('||')[4]
            mention = mention.strip()
            if '|' in mention:
                mention = mention.split('|')
                for m_id in mention:
                    mentions.append(m_id)
            else:
                mentions.append(mention)
    elif input_type == 'dict':
        for line in text:
            mention = line.split('||')[0]
            mention = mention.strip()
            if '|' in mention:
                mention = mention.split('|')
                for m_id in mention:
                    mentions.append(m_id)
            else:
                mentions.append(mention)
    return mentions

def get_concepts(input_texts,input_type='query'):
    concepts = []
    for input_text in input_texts:
        with open(os.path.abspath(input_text) ,'r') as f:
            text = f.readlines()
            _concepts = query_parse(text,input_type)
            for concept in _concepts:
                if concept not in concepts:
                    concepts.append(concept)
    return concepts


def get_ui_data(ui,auth_client):
    apikey = 'b8d21590-1cf7-4b92-b3be-04de3d7e99ec'
    tgt = auth_client.gettgt()
    uri = "https://uts-ws.nlm.nih.gov/rest"
    content_endpoint = '/content/current/source/MSHFRE/{}/atoms'.format(ui)
    '''
    query = {'ticket':AuthClient.getst(tgt),
            'string':ui,
            'inputType':'sourceUi',
            'sabs':'MSH',
            'searchType':'exact'
    }
    '''
    query={'ticket':auth_client.getst(tgt),}
    r = requests.get(uri+content_endpoint,params=query)
    r.encoding = 'utf-8'
    items  = json.loads(r.text)
    names=[]
    try:
        results = items["result"]
    except KeyError:
        print(ui)
        return
    for result in results:
        names.append(result['name'])
    return names

def get_fr_query(query_ids,auth_client):
    mentions = []
    for i, q_id in enumerate(query_ids):
        if i % 100 == 0:
            print(i)
        names = get_ui_data(q_id,auth_client)
        try:
            for name in names:
                mentions.append('{}||{}'.format(q_id,name))
        except TypeError:
            continue
    return mentions

def merge_dict():
    input_dict_mentions = []
    with open(args.input_dict,'r') as f:
        input_dict_mentions = f.readlines()
    for i,mention in enumerate(input_dict_mentions):
        input_dict_mentions[i] = mention.strip() 
    dict_mentions = input_dict_mentions + fr_query        
    with open(output_dir + '{}'.format('/') + 'fr_merged_train_dictionary.txt','w') as g:
        for i,mention in enumerate(dict_mentions):
            if i != (len(dict_mentions) - 1):
                g.write(mention + '\n')
            else:
                g.write(mention)

def main(args):
    apikey = 'b8d21590-1cf7-4b92-b3be-04de3d7e99ec'
    input_dir = args.input_dir
    output_dir = args.output_dir
    input_texts = sorted(glob.glob(os.path.join(input_dir, "*.concept")))
    query_ids = get_concepts(input_texts)
    auth_client = Authentication(apikey)
    fr_query =get_fr_query(query_ids,auth_client)
    #de_query = get_de_query(query_ids)

if __name__ == '__main__':
  args = parse_args()
  main(args)