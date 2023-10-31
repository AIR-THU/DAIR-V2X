import os
from tools.dataset_converter.utils import write_txt


def gen_ImageSet(target_root, split_info, sensor_view="vehicle"):
    target_ImageSets_path = f'{target_root}/ImageSets'
    if not os.path.exists(target_ImageSets_path):
        os.makedirs(target_ImageSets_path)
    test_file = ""
    train_file = ""
    val_file = ""

    sensor_view = sensor_view + "_split"
    split_data = split_info[sensor_view]
    for i in range(len(split_data["train"])):
        name = split_data["train"][i]
        train_file = train_file + name + "\n"

    for i in range(len(split_data["val"])):
        name = split_data["val"][i]
        val_file = val_file + name + "\n"

    # The test part of the dataset has not been released
    # for i in range(len(split_data["test"])):
    #     name = split_data["test"][i]
    #     test_file = test_file + name + "\n"

    trainval_file = train_file + val_file

    write_txt(os.path.join(target_ImageSets_path, "test.txt"), test_file)
    write_txt(os.path.join(target_ImageSets_path, "trainval.txt"), trainval_file)
    write_txt(os.path.join(target_ImageSets_path, "train.txt"), train_file)
    write_txt(os.path.join(target_ImageSets_path, "val.txt"), val_file)

