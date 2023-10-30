import os
from tools.dataset_converter.utils import write_txt


def gen_ImageSet(target_root, split_info):
    target_ImageSets_path = f'{target_root}/ImageSets'
    if not os.path.exists(target_ImageSets_path):
        os.makedirs(target_ImageSets_path)

    list_train_seqs = split_info["batch_split"]["train"]
    list_val_seqs = split_info["batch_split"]["val"]
    list_trainval_seqs = list_train_seqs + list_val_seqs
    list_test_seqs = split_info["batch_split"]["test"]
    list_train_seqs.sort()
    list_val_seqs.sort()
    list_trainval_seqs.sort()
    list_test_seqs.sort()

    str_train_seqs = ""
    str_val_seqs = ""
    str_trainval_seqs = ""
    str_test_seqs = ""

    for train_seq in list_train_seqs:
        str_train_seqs = str_train_seqs + train_seq + "\n"
    for val_seq in list_val_seqs:
        str_val_seqs = str_val_seqs + val_seq + "\n"
    for trainval_seq in list_trainval_seqs:
        str_trainval_seqs = str_trainval_seqs + trainval_seq + "\n"
    for test_seq in list_test_seqs:
        str_test_seqs = str_test_seqs + test_seq + "\n"

    write_txt(target_ImageSets_path + "/train.txt", str_train_seqs)
    write_txt(target_ImageSets_path + "/val.txt", str_val_seqs)
    write_txt(target_ImageSets_path + "/trainval.txt", str_trainval_seqs)
    write_txt(target_ImageSets_path + "/test.txt", str_test_seqs)

