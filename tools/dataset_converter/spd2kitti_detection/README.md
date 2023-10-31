# Convert SPD to KITTI format

## Install pypcd

```bash
git clone https://github.com/klintan/pypcd.git
cd pypcd/ 
python setup.py install
```

## SPD -> KITTI

```bash
python tools/dataset_converter/dair2kitti.py \
--source-root data/SPD/cooperative-vehicle-infrastructure/vehicle-side \
--target-root data/KITTI/cooperative-vehicle-infrastructure/vehicle-side \
--split-path data/split_datas/cooperative-split-data-spd.json \
--label-type lidar \
--sensor-view vehicle \
--no-classmerge
```

````bash
python tools/dataset_converter/dair2kitti.py \
--source-root data/SPD/cooperative-vehicle-infrastructure/infrastructure-side \
--target-root data/KITTI/cooperative-vehicle-infrastructure/infrastructure-side \
--split-path data/split_datas/cooperative-split-data-spd.json \
--label-type lidar \
--sensor-view infrastructure \
--no-classmerge
````
