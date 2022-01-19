mkdir processed_pairs
mkdir processed_pairs/test
mkdir processed_pairs/train
python3 process.py --file_list test/test_file_list.txt --annotation_paths gold/test_norm/ --note_paths test/test_note/ --save_to processed_pairs/test/
python3 process.py --file_list train/train_file_list.txt --annotation_paths train/train_norm/ --note_paths train/train_note/ --save_to processed_pairs/train/

