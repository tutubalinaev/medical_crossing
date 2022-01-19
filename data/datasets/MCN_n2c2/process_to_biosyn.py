from glob import glob
from nltk.tokenize import word_tokenize
import os
from argparse import ArgumentParser

def parse_annotation_line(line):
  # id||cui||char start||char end
  splitted_line = line.strip().split('||')
  annotation = {'id': splitted_line[0], 'cui':splitted_line[1], 'start_positions':[], 'end_positions': []}
  for i in range(2, len(splitted_line), 2):
    annotation['start_positions'].append(int(splitted_line[i]))
    annotation['end_positions'].append(int(splitted_line[i+1]))
  return annotation


def read_note(note_path):
  with open(note_path, encoding='utf-8') as input_stream:
    note = input_stream.read()
  return note


def read_annotations(annotation_path):
  with open(annotation_path, encoding='utf-8') as input_stream:
    annotations = [parse_annotation_line(line) for line in input_stream]
  return annotations


def get_n_words_from_context(context, left, n):
  tokenized_context = word_tokenize(context)
  if left:
    n_words = tokenized_context[-n:]
  else:
    n_words = tokenized_context[:n]
  return ' '.join(n_words)


def get_mention(note, annotation):
  entity = ''
  for start, end in zip(annotation['start_positions'], annotation['end_positions']):
    entity += note[start:end]
  return entity


def f(note, annotations, context_size):
  entities = []
  labels = []
  left_contexts = []
  right_contexts = []
  for annotation in annotations:
    entity = get_mention(note, annotation)
    entities.append(entity)
    labels.append(annotation['cui'])
    left_context = note[:annotation['start_positions'][0]]
    right_context = note[annotation['start_positions'][-1]:]
    left_contexts.append(get_n_words_from_context(left_context, True, context_size))
    right_contexts.append(get_n_words_from_context(right_context, False, context_size))
  return entities, labels, left_contexts, right_contexts

if __name__ == '__main__':
  parser = ArgumentParser()
  parser.add_argument('--file_list',default='test/test_file_list.txt')
  parser.add_argument('--annotation_paths',default='test/test_norm_cui_replaced_with_unk/')
  parser.add_argument('--note_paths',default='test/test_note/')
  parser.add_argument('--label')
  args = parser.parse_args()
  
  with open(args.file_list, encoding='utf-8') as input_stream:
    files_list = [line.strip() for line in input_stream]
  annotation_paths = [os.path.join(args.annotation_paths, fl) + '.norm' for fl in files_list]
  note_paths = [os.path.join(args.note_paths, fl) + '.txt' for fl in files_list]
  med_entities = []
  labels = []
  left_contexts = []
  right_contexts = []
  context_size = 20
  for annotation_path, note_path in zip(annotation_paths, note_paths):
    print("Parsed", annotation_path, note_path)
    note = read_note(note_path)
    annotations = read_annotations(annotation_path)
    medents, lbls, lcontexts, rcontexts = f(note, annotations, context_size)
    med_entities += medents
    labels += lbls
    left_contexts += lcontexts
    right_contexts += rcontexts
  with open(args.label+'_med_entities.txt', 'w', encoding='utf-8') as med_entities_output_stream, \
   open(args.label+'_labels.txt', 'w', encoding='utf-8') as labels_output_stream, \
   open(args.label+'_left_contexts.txt', 'w', encoding='utf-8') as lcontexts_output_stream, \
   open(args.label+'_right_contexts.txt', 'w', encoding='utf-8') as rcontexts_output_stream:
    for entity, label, lcontext, rcontext in zip(med_entities, labels, left_contexts, right_contexts):
      med_entities_output_stream.write(entity.replace('\n', ' ') + '\n')
      labels_output_stream.write(label + '\n')
      lcontexts_output_stream.write(lcontext.replace('\n', ' ') + '\n')
      rcontexts_output_stream.write(rcontext.replace('\n', ' ') + '\n')
