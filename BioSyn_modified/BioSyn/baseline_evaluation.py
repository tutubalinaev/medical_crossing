from utils import (
  evaluate_topk_acc
)
import json
import argparse
import os

def parse_args():
  """
  Parse input arguments
  """
  parser = argparse.ArgumentParser(description='accuracy evaluation')
  # Required
  parser.add_argument('--predictions', required=True, help='Path to json file with predictions')
  parser.add_argument('--output_dir', help='path to the output directory')
  args = parser.parse_args()
  return args

def main(args):
  accuracy = {}
  types = ['sparse evalset','dense evalset','hybrid evalset']

  with open(args.predictions) as f:
    predicts = json.load(f)
  for predict_type in types:
    result = evaluate_topk_acc(predicts[predict_type])
    accuracy[predict_type]={'acc@1':result['acc1'], 'acc@5':result['acc5']}
  output_file = os.path.join(args.output_dir,"accuracy.json")
  with open(output_file, 'w') as f:
    json.dump(accuracy, f, indent=4)
  


if __name__ == '__main__':
  args = parse_args()
  main(args)
