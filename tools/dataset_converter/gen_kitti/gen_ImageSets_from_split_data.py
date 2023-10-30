import os
from tools.dataset_converter.utils import read_json, mkdir_p, write_txt


def gen_ImageSet_from_split_data(ImageSets_path, split_data_path, sensor_view="vehicle"):
    split_data = read_json(split_data_path)
    test_file = ""
    train_file = ""
    val_file = ""

    if "vehicle_split" in split_data.keys():
        sensor_view = sensor_view + "_split"
        split_data = split_data[sensor_view]
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

    mkdir_p(ImageSets_path)
    write_txt(os.path.join(ImageSets_path, "test.txt"), test_file)
    write_txt(os.path.join(ImageSets_path, "trainval.txt"), trainval_file)
    write_txt(os.path.join(ImageSets_path, "train.txt"), train_file)
    write_txt(os.path.join(ImageSets_path, "val.txt"), val_file)
