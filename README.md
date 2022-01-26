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
1. UMLS data, precisely: `MRCONSO.RRF`, `MRSTY.RRF`
2. CLEF2013 eHealth Task 1 data: [link](https://sites.google.com/site/shareclefehealth/)
3. CANTEMIST vocabulary used by [SINAI research group team](http://ceur-ws.org/Vol-2664/cantemist_paper1.pdf). 
The file 'cieo-synonyms.csv' is available on request.
4. MCN data introduced in [the original paper](https://doi.org/10.1016/j.jbi.2019.103132). 
5. [optional] MedLexSp.zip, which is [available on request](http://www.lllf.uam.es/ESP/nlpmedterm_en.html#deliverables) 
and requires signing papers.

### Preparing vocabularies

1. Put `MRCONSO.RRF`, `MRSTY.RRF` and `MedLexSp.zip` into the root of the repository.
2. To generate the English vocabulary used for MCN dataset, run `./generate_snomedct_all.sh`. This would 
generate `data/vocabs/SNOMEDCT_US-all-aggregated.txt`, a large file.
3. English vocabulary used specifically for CLEF2013 (disorders only!):
run `vocab_generate_snomedct_clef2013.sh`. This would generate `data/vocabs/SNOMEDCT_US_clef2013-biosyn-aggregated.txt`.
4. Spanish vocabulary for CANTEMIST: run `vocab_generate_cantemist_lopez_ubeda_et_al.sh`. 
This generates `data/vocabs/CANTEMIST-lopez-ubeda-et-al.txt`. `cieo-synonyms.csv` should be at the root of the repo. 
5. CodiEsp vocabularies: run `vocab_generate_icd10_codiesp.sh`; [zenodo_get](https://pypi.org/project/zenodo-get/) 
Python package tool should be installed. Files `data/vocabs/codiesp-d-codes-es.txt` and 
`data/vocabs/codiesp-p-codes-es.txt` are generated as a result.
6. MANTRA vocabularies: run **NEED INPUT FROM DMITRY**.
7. [optional] To prepare MedLexSp, run `vocab_generate_medlexsp.sh`; file `data/vocabs/MedLexSp_v0.txt` should be generated.

### Preparing datasets
 
1. CANTEMIST: simply run `data_generate_cantemist.sh`; `zenodo_get` is required. The results will be 
saved into `data/datasets/cantemist`.
2. MCN: **TODO**
3. CLEF2013 eHealth: the original data is in `*.json` format. Pass the path to the folder containing `train.json` 
and `test.json` (should not be `data/datasets/clef2013ehealth`) as the only arg to `data_generate_clef2013.sh`.
4. CodiEsp: run `data_generate_codiesp.sh` (requires `zenodo_get`), the results will be written to `data/datasets/codiesp`.
5. MANTRA: **TODO**


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

**TODO**

## Other

## References to the works used

### Datasets & vocabularies

* CodiEsp: Clinical Case Coding in Spanish Shared Task (eHealth CLEF 2020) -- https://temu.bsc.es/codiesp/
* MCN: The 2019 n2c2/UMass Track 3 -- https://n2c2.dbmi.hms.harvard.edu/2019-track-3 
* CANTEMIST (CANcer TExt Mining Shared Task – tumor named entity recognition -- https://temu.bsc.es/cantemist/
* Mantra GSC -- http://biosemantics.org/mantra/ https://files.ifi.uzh.ch/cl/mantra/gsc/GSC-v1.1.zip 
* **TODO**
