# Steps for processing of MedMentions

## Required files:
- corpus_pubtator_st21pv.txt ([source](https://github.com/chanzuckerberg/MedMentions/tree/master/st21pv/data))
- corpus_pubtator_pmids_dev/test/trng.txt ([source](https://github.com/chanzuckerberg/MedMentions/tree/master/full/data))
- SemGroups.txt ([source](https://semanticnetwork.nlm.nih.gov/download/SemGroups.txt))
- MRCONSO.RRF
- cui_to_type.json

## Steps
1. **input_create.py**  
Input: corpus_pubtator_st21pv.txt, SemGroups.txt  
Output: mm_st21pv_input.concept

2. **dict_create.py**  
Input: MRCONSO.RRF  
Output: mm_st21pv_dict.txt

3. **corpus_to_ab3p.py**  
Input: corpus_pubtator_st21pv.txt  
Output: ab3p_result.txt

4. **input_preprocess.py**  
Input: ab3p_result.txt, mm_st21pv_input.concept, mm_st21pv_dict.txt  
Output: mm_st21pv_input_prep.concept

5. **input_filter.py**  
Input: mm_st21pv_input_prep.concept  
Output: mm_st21pv_input_prep_DISO.concept (e.g., DISO - target group)

6. **dict_filter.py**  
Input: cui_to_type.json, SemGroups.txt  
Output: m_st21pv_dict_DISO.txt (e.g., DISO - target group)

7. **input_train_test_split.py**  
Input: corpus_pubtator_pmids_dev/test/trng.txt, mm_st21pv_input_prep_DISO.concept (e.g., DISO - target group)  
Output: mm_st21pv_input_prep_DISO_dev/test/train.concept (e.g., DISO - target group)
