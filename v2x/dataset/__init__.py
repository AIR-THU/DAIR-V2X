from dair_v2x_for_detection import *
from dair_v2x_for_detection_v2 import *
from dataset_utils import *

SUPPROTED_DATASETS = {
    "dair-v2x-v": DAIRV2XV,
    "dair-v2x-i": DAIRV2XI,
    "vic-sync": VICSyncDataset,
    "vic-async": VICAsyncDataset,
    "dair-v2x-v-v2": DAIRV2XVV2,
    "dair-v2x-i-v2": DAIRV2XIV2,
    "vic-sync-v2": VICSyncDatasetV2,
    "vic-async-v2": VICAsyncDatasetV2,
}
