# coding: utf-8

from argparse import ArgumentParser

import pandas as pd


def read_mrconso(fpath):
    """
    see https://www.ncbi.nlm.nih.gov/books/NBK9685/table/ch03.T.concept_names_and_sources_file_mr/?report=objectonly
    example C0000005|FRE|S|L6215648|PF|S7133916|Y|A27488794||M0019694|D012711|MSHFRE|ET|D012711|MAA-I 131|3|N||
    """
    columns = ['CUI', 'LAT', 'TS', 'LUI', 'STT', 'SUI', 'ISPREF', 'AUI', 'SAUI', 'SCUI', 'SDUI', 'SAB', 'TTY', 'CODE',
               'STR', 'SRL', 'SUPPRESS', 'CVF', 'NOCOL']
    return pd.read_csv(fpath, names=columns, sep='|', encoding='utf-8')


def read_mrsty(fpath):
    columns = ['CUI', 'TUI', 'STN', 'STY', 'ATUI', 'CVF', 'NOCOL']
    return pd.read_csv(fpath, names=columns, sep='|', encoding='utf-8')


def read_mrrel(fpath):
    """
        see https://www.ncbi.nlm.nih.gov/books/NBK9685/table/ch03.T.related_concepts_file_mrrel_rrf/?report=objectonly
        example C0002372|A0022283|AUI|SY|C0002372|A16796726|AUI||R55153988||RXNORM|RXNORM|||N||
    """
    columns = ['CUI1', 'AUI1', 'STYPE1', 'REL', 'CUI2', 'AUI2', 'STYPE2', 'RELA', 'RUI', 'SRUI', 'SAB', 'VSAB', 'SL',
               'RG', 'DIR', 'SUPPRESS', 'CVF']
    return pd.read_csv(fpath, names=columns, sep='|', encoding='utf-8')


if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument('--mrconso')
    parser.add_argument('--mrsty')
    parser.add_argument('--types', nargs='+', default=[])
    parser.add_argument('--lang', default='ENG')
    parser.add_argument('--ontology', default=None, nargs='+')
    parser.add_argument('--concept_id_column', default='CUI')
    parser.add_argument('--save_to')
    parser.add_argument('--save_all', action='store_true')
    args = parser.parse_args()

    mrconso = read_mrconso(args.mrconso)

    if len(args.types) > 0:
        mrsty = read_mrsty(args.mrsty)
        filtered_concepts = mrsty[mrsty.TUI.isin(args.types)]['CUI'].drop_duplicates()
        filtered_umls = mrconso[(mrconso.CUI.isin(filtered_concepts)) & (mrconso.LAT == args.lang)]
    else:
        filtered_umls = mrconso[mrconso.LAT == args.lang]

    if args.ontology is not None:
        filtered_umls = filtered_umls[filtered_umls.SAB.isin(args.ontology)]

    final = filtered_umls

    if not args.save_all:
        final = final[[args.concept_id_column, 'STR']]

    final['STR'] = final.STR.str.lower()
    final = final.groupby('STR')['CUI'].apply('|'.join).reset_index()

    with open(args.save_to, 'w', encoding='utf-8') as output_stream:
        for row_idx, row in final.iterrows():
            output_stream.write(f"{row['CUI']}||{row['STR']}\n")
