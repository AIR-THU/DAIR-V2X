import argparse
import os
from v2x_utils.gen_eval_tracking_data import convert_gt_label, convert_track_label
from AB3DMOT_plugin.scripts.KITTI.evaluate import evaluate
from AB3DMOT_plugin.scripts.KITTI.mailpy import Mail


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--track-eval-gt-path", type=str, help="Path to ground truth for V2X-Seq-SPD track evaluation in KITTI format"
    )
    parser.add_argument(
        "--track-results-path", type=str, help="Path to tracking results"
    )
    parser.add_argument(
        "--track-eval-output-path", type=str, help="Path to tracking evaluation results"
    )
    parser.add_argument(
        "--ab3dmot-path", type=str, default="AB3DMOT_plugin", help="Path to AB3DMOT"
    )
    parser.add_argument(
        "--fusion-method",
        type=str,
        choices=["early_fusion", "middle_fusion", "late_fusion", "ffnet", "veh_only", "inf_only"],
        help="Model type",
    )
    parser.add_argument('--split', type=str, default='val', help='train, val, test')
    parser.add_argument('--det-name', type=str, default='imvoxelnet', help='imvoxelnet')
    parser.add_argument('--cat', type=str, default='Car', help='category of running tracking')
    parser.add_argument(
        "--tvt",
        nargs="+",
        type=str,
        default=["validation"],
        choices=["training", "validation", "testing"],
        help="Train, validation, or test",
    )
    return parser.parse_args()


def main(args):
    extended_range = [0, -39.68, -3, 100, 39.68, 1]
    file_type = f'{args.det_name}_{args.cat}_{args.split}_H1'
    for tvt in args.tvt:
        print("Track evaluation")
        # 生成eval格式ground truth label及val_dic_new_frame2id_frame.json
        kitti_track_tvt_path = os.path.join(args.track_eval_gt_path, "cooperative", tvt)
        print("generate eval gt label")
        dict_seq_frame2id = convert_gt_label(kitti_track_tvt_path, args.ab3dmot_path, extended_range)

        # 生成eval格式track label
        print("Convert track result")
        track_results_path = f'{args.track_results_path}/{file_type}/data_0'
        ab3dmot_results_dir = f'{args.ab3dmot_path}/results/KITTI/{file_type}/data_0'
        convert_track_label(track_results_path, ab3dmot_results_dir, dict_seq_frame2id, extended_range)

        # get unique sha key of submitted results
        num_hypo = "1"
        dimension = "3D"
        thres = 0.25
        mail = Mail("")
        #

        if dimension == '2D':
            eval_3diou, eval_2diou = False, True  # eval 2d
        elif dimension == '3D':
            eval_3diou, eval_2diou = True, False  # eval 3d
        else:
            eval_3diou, eval_2diou = True, False  # eval 3d

        # evaluate results
        success = evaluate(file_type, mail, num_hypo, eval_3diou, eval_2diou, thres)

        os.system(f'mv {args.ab3dmot_path}/results/KITTI/{file_type} {args.track_eval_output_path}')


if __name__ == "__main__":
    args = parse_arguments()
    main(args)
