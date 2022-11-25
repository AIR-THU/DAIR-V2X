the resulting .json file should contain the following information in dict:
* "boxes_3d":  3D coordinate values of 8 vertices of all prediction boxes in the current frame, based on Vehicle LiDAR Coordinate System;
* "labels_3d": The category of all prediction boxes in the current frame;
* "scores_3d": indicates the confidence of all prediction boxes in the current frame;
* "ab_cost":   indicates the current frame transmission cost;
The current frame transmission cost calculation method can refer to send() in https://github.com/AIR-THU/DAIR-V2X/blob/main/v2x/models/model_utils/channel.py.

An Result Example of 010823.json (there are two detection boxes):


{
‘boxes_3d’:

    [[[ 1.00691042e+01,  3.46455169e+00, -1.93001246e+00],
    [ 1.00691042e+01,  3.46455169e+00, -3.84817839e-01],
    [ 1.00456753e+01,  5.61096096e+00, -3.84817839e-01],
    [ 1.00456753e+01,  5.61096096e+00, -1.93001246e+00],
    [ 1.46534252e+01,  3.51459002e+00, -1.93001246e+00],
    [ 1.46534252e+01,  3.51459002e+00, -3.84817839e-01],
    [ 1.46299963e+01,  5.66099930e+00, -3.84817839e-01],
    [ 1.46299963e+01,  5.66099930e+00, -1.93001246e+00]],
	      
    [[ 2.98359299e+01,  4.95744991e+00, -1.65398097e+00],
    [ 2.98359299e+01,  4.95744991e+00, -1.67575479e-01],
    [ 2.98803558e+01,  6.82962942e+00, -1.67575479e-01],
    [ 2.98803558e+01,  6.82962942e+00, -1.65398097e+00],
    [ 3.40029182e+01,  4.85857058e+00, -1.65398097e+00],
    [ 3.40029182e+01,  4.85857058e+00, -1.67575479e-01],
    [ 3.40473442e+01,  6.73075008e+00, -1.67575479e-01],
    [ 3.40473442e+01,  6.73075008e+00, -1.65398097e+00]]],

‘labels_3d’: [2, 2],

‘scores_3d’: [0.9015367 , 0.87085658],

‘ab_cost’: 123456

}
