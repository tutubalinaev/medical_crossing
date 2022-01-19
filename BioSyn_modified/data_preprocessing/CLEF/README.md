1) Prepare dirs with source data format and full medical notes. Default it Task1TrainSetGOLD200pipe and TrainSetCorpus200EvaluationWorkbench
2) Run clef_preprocess.py
3) Run folowing commang from BioSyn repository
```
$ python preprocess/query_preprocess.py --input_dir ../../CLEF/TrainSetCorpus200EvaluationWorkbench/ --output_dir ../../CLEF/processed --ab3p_path ../Ab3P/identify_abbr --lowercase true --remove_punctuation true --resolve_composites
```
4) Run collect_concepts.py
5) Run clef_dictionary_creation.py> You must provide MRCONSO.RRF to the root dir. It can be downloaded from out Google Storage
6) Run folowing commang from BioSyn repository
```
python preprocess/dictionary_preprocess.py --input_dictionary_path ../../CLEF/dictionary.txt --output_dictionary_path ../../CLEF/dictionary_processed.txt  --lowercase
```
7) Finally, run clef_dataset_splitter.py
