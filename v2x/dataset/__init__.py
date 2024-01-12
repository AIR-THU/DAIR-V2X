from dair_v2x_for_detection import *
from dair_v2x_for_detection_spd import *
from dataset_utils import *

SUPPROTED_DATASETS = {
    "dair-v2x-v": DAIRV2XV,
    "dair-v2x-i": DAIRV2XI,
    "vic-sync": VICSyncDataset,
    "vic-async": VICAsyncDataset,
    "dair-v2x-v-spd": DAIRV2XVSPD,
    "dair-v2x-i-spd": DAIRV2XISPD,
    "vic-sync-spd": VICSyncDatasetSPD,
    "vic-async-spd": VICAsyncDatasetSPD,
}
