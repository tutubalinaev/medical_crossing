# Medical Crossing: X-Lingual Clinical Concept Normalization Benchmark

This repository contains scripts automating the evaluation of clinical entity linking 
tasks in multiple languages.

The underlying philosophy is the following.

* It is better to *submodule* the code than copy it.
* ...And write a wrapper for eval scripts rather than change the original tool's code,
* We assume that Python eval scripts usually need 
  * core parameters commonly shared by many model implementations and
  * custom parameters specific for this particular model (or model implementation).
* Therefore we need mappings between shared parameters <-> some DSL of our own.

All this should be done using a single script and be configurable via Hydra.

---

## Overview of the repository

In general, evaluation is done with running `universal_runner.py` script, 
which takes hydra-style command line arguments as input. The set of possible
parameters and default values are configured using YAML files in the `config/` folder.

Each run is saved to `results/sessions_YYYY-MM-DD-...` with the corresponding YAML config.

To aggregate the results, `universal_aggregator.py` is run; it applies to each session's
 folder in the `results` a relevant output parser (set in `model/*.yaml`; code in `untils.output_parsers`).
 
As a result, a large CSV table is generated; a row per each set of params. The latest scores are kept in case 
of duplicate parameters sets.

### Configs folder

```
config/
└─── dataset/
|    │   ...
|    │   # datasets YAML configs specifying [names, paths, languages, fairness level]
└─── model/
|    │   ...
|    │   # models YAML configs specifying [names, output parsers, model_path, parameters_mapping]
└─── parameters_mapping/
|    │   ...
|    │   # mappings of different arguments sets in the form "our DSL: custom_args", e.g. "data_directory: data_dir"
└─── vocabulary/
|    │   ...
|    │   # vocabularies YAML configs specifying [names, paths]
|    config.yaml
```   

## How to setup the benchmarks

### Required manual work for preparing this benchmark

Unfortunately, these benchmarks require a few steps that cannot be automated;
certain datasets are available only on request after certain formal procedures.

One should obtain
1. Several corpora: CANTEMIST, MCN, Mantra GSC, CodiEsp (see Section "Datasets & Vocabularies")
1. UMLS 2020AA data, precisely: `MRCONSO.RRF`, `MRSTY.RRF`
2. CANTEMIST vocabulary used by [SINAI research group team](http://ceur-ws.org/Vol-2664/cantemist_paper1.pdf). 
The file 'cieo-synonyms.csv' is available on request to authors.
3. MCN data introduced in [the original paper](https://doi.org/10.1016/j.jbi.2019.103132). 
4. [optional] MedLexSp.zip, which is [available on request](http://www.lllf.uam.es/ESP/nlpmedterm_en.html#deliverables) 
and requires signing papers.

### Preparing vocabularies

1. Put `MRCONSO.RRF`, `MRSTY.RRF` and [optional] `MedLexSp.zip` into the root of the repository.
2. To generate the English vocabulary used for MCN dataset, run `./vocab_generate_snomedct_all.sh`. This would 
generate `data/vocabs/SNOMEDCT_US-all-aggregated.txt`, a large file.

Expected output:
```1324661 data/vocabs/SNOMEDCT_US-all-aggregated.txt```

3. English vocabulary used specifically for CLEF2013 (disorders only!):
run `./vocab_generate_snomedct_clef2013.sh`. This would generate `data/vocabs/SNOMEDCT_US_clef2013-biosyn-aggregated.txt`.

Expected output:
```363326 data/vocabs/SNOMEDCT_US_clef2013-biosyn-aggregated.txt```

4. Spanish vocabulary for CANTEMIST: run `./vocab_generate_cantemist_lopez_ubeda_et_al.sh`. 
This generates `data/vocabs/CANTEMIST-lopez-ubeda-et-al.txt`. `cieo-synonyms.csv` should be at the root of the repo. 
5. CodiEsp vocabularies: run `./vocab_generate_icd10_codiesp.sh`; [zenodo_get](https://pypi.org/project/zenodo-get/) 
Python package tool should be installed. Files `data/vocabs/codiesp-d-codes-es.txt` and 
`data/vocabs/codiesp-p-codes-es.txt` are generated as a result.
6. **TODO:** MANTRA vocabularies:  run `./vocab_generate_mantra.sh`.
7. To generate UMLS French DISO vocabulary run `./vocab_generate_umls_fre_diso.sh`. This would generate `data/vocabs/umls_fre_diso.txt`.
8. [optional] To prepare MedLexSp, run `./vocab_generate_medlexsp.sh`; file `data/vocabs/MedLexSp_v0.txt` should be generated.


### Preparing datasets
 
1. CANTEMIST: simply run `./data_generate_cantemist.sh`; `zenodo_get` is required. The results will be 
saved into `data/datasets/cantemist`.
2. MCN: the data can be downloaded [here](https://portal.dbmi.hms.harvard.edu/projects/n2c2-2019-t3/), after the registration.
3. CodiEsp: run `./data_generate_codiesp.sh` (requires `zenodo_get`), the results will be written to `data/datasets/codiesp`.
4. MANTRA: **TODO**

### Filtering datasets

Example:

```bash
python3 fairification.py --test_dir data/datasets/codiesp/DIAGNOSTICO/test \
                          --train_dir data/datasets/codiesp/DIAGNOSTICO/train \
                          --vocabulary data/vocabs/codiesp-d-codes-es.txt \
                          --levenshtein_norm_method 1 \
                          --levenshtein_threshold 0.2
```

This may take a while; should generate folders:
```
data/
└─── datasets/
|    └─── codiesp/
|    |    └─── DIAGNOSTICO/
|    |    |    test-fair_exact/
|    |    |    ... 
|    |    |    test-fair_exact_vocab/
|    |    |    ... 
|    |    |    test-fair_levenshtein_0.2/
|    |    |    ... 
|    |    |    test-fair_levenshtein_train_0.2/
|    |    |    ... 
```


## Evaluation without pretraining

For running a unifying evaluation script, run e.g. as follows:

```bash
    python3.6 universal_runner.py 
```

The default params can be configured in `config/` directory.

## Generating evaluation scripts for multiple settings

## Statistics aggregation

All the results are reported in separate folders. To build a single *.CSV sheet with the results,
run the script

```bash 
python3.6 universal_aggregator.py
```

## Setting up a Docker image

```bash
    cd medical_crossing/
    docker build . -t medical_crossing  
    nvidia-docker run -p 8807:8807 -v "`pwd`:/root/medical_crossing/" -it medical_crossing:latest bash
```

## References to the works used

### Datasets & vocabularies

* [CodiEsp](https://temu.bsc.es/codiesp/): Clinical Case Coding in Spanish Shared Task (eHealth CLEF 2020)
* [MCN](https://n2c2.dbmi.hms.harvard.edu/2019-track-3): The 2019 n2c2/UMass Track 3
* [CANTEMIST](https://temu.bsc.es/cantemist/) (CANcer TExt Mining Shared Task – tumor named entity recognition 
* [Mantra GSC](https://files.ifi.uzh.ch/cl/mantra/gsc/GSC-v1.1.zip), [link](http://biosemantics.org/mantra/)
* [optional] MedLexSp.zip
* UMLS 2020AA
* **TODO**
