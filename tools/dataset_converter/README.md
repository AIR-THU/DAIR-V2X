# Affine transformation of coordinate system

## Transformation Matrix

### Rotation Matrix

Rotate around the x-axis, y-axis and z-axis respectively, and multiply the three rotation matrices to obtain the rotation matrix at any angle in 3D space. (Right-handed coordinate system)

When rotating around the x-axis, it can be seen as a rotation on the 2D plane of yoz, at which time the value of x remains unchanged.

$$
R_x
=
\begin{bmatrix}
1& 0&0
\\
0&cos\theta_x&sin\theta_x
\\
0&-sin\theta_x&cos\theta_x
\end{bmatrix}
$$

When rotating around the y-axis, it can be seen as a rotation on the 2D plane of zox, at which time the value of y remains unchanged.

$$
R_y
=
\begin{bmatrix}
cos\theta_y&0&-sin\theta_y
\\
0&1&0
\\
sin\theta_y&0&cos\theta_y
\end{bmatrix}
$$

When rotating around the z-axis, it can be seen as a rotation on the 2D plane of xoy, at which time the value of z remains unchanged.

$$
R_z
=
\begin{bmatrix}
cons\theta_z&sin\theta_z&0
\\
-sin\theta_z&cos\theta_z&0
\\
0&0&1
\end{bmatrix}
$$

The final 3D rotation matrix is the multiplication of the above three matrices.

$$
R=R_xR_yR_z
=
\begin{bmatrix}
1&0&0
\\
0&cos\theta_x&sin\theta_x
\\
0&-sin\theta_x&cos\theta_x
\end{bmatrix}
\begin{bmatrix}
cos\theta_y&0&-sin\theta_y
\\
0&1&0
\\
sin\theta_y&0&cos\theta_y
\end{bmatrix}
\begin{bmatrix}
cons\theta_z&sin\theta_z&0
\\
-sin\theta_z&cos\theta_z&0
\\
0&0&1
\end{bmatrix}
$$

### Translation Matrix

Translate along the x-axis direction, y-axis direction and z-axis direction respectively, and add the three translation matrices to obtain any translation matrix in 3D space.

When translating along the x-axis direction, it can be seen that each point is translated along the x-axis direction. At this time, the values of y and z remain unchanged.

$$
T_x=
\begin{bmatrix}
\Delta_x
\\
0
\\
0
\end{bmatrix}
$$

When translating along the y-axis direction, it can be seen that each point is translated along the y-axis direction. At this time, the values of z and x remain unchanged.

$$
T_y=
\begin{bmatrix}
0
\\
\Delta_y
\\
0
\end{bmatrix}
$$

When translating along the z-axis direction, it can be seen that each point is translated along the z-axis direction. At this time, the values of x and y remain unchanged.

$$
T_z=
\begin{bmatrix}
0
\\
0
\\
\Delta_z
\end{bmatrix}
$$

The final 3D translation matrix is the sum of the above three matrices.

$$
T=
T_x+T_y+T_z
=
\begin{bmatrix}
\Delta_x
\\
\Delta_y
\\
\Delta_z
\end{bmatrix}
$$

## Related Codes

### 7 Dimensions Vector Representation to 8 Corner Points Representation

```Python
def get_lidar_3d_8points(label_3d_dimensions, lidar_3d_location, rotation_z):
    """
          4 -------- 5      
         /|         /|     
        7 -------- 6 .     
        | |        | |     
        . 0 -------- 1     
        |/         |/     
        3 -------- 2
        forward direction: 3 -> 0
        Args: 
            label_3d_dimensions: [l, w, h]
            lidar_3d_location: [x, y, z]
            rotation_z: rotation
    """
    lidar_rotation = np.matrix(
        [
            [math.cos(rotation_z), -math.sin(rotation_z), 0],
            [math.sin(rotation_z), math.cos(rotation_z), 0],
            [0, 0, 1]
        ]
    )
    l, w, h = label_3d_dimensions
    corners_3d_lidar = np.matrix(
        [
            [l / 2, l / 2, -l / 2, -l / 2, l / 2, l / 2, -l / 2, -l / 2],
            [w / 2, -w / 2, -w / 2, w / 2, w / 2, -w / 2, -w / 2, w / 2],
            [-h / 2, -h / 2, -h / 2, -h / 2, h / 2, h / 2, h / 2, h / 2],
        ]
    )
    lidar_3d_8points = lidar_rotation * corners_3d_lidar + np.matrix(lidar_3d_location).T
    return lidar_3d_8points.T.tolist()
```

7 Dimensions Vector [l, w, h, x, y, z, rotation] can be obtained from the json files in the following directory:

* `data/DAIR-V2X-V2/cooperative-vehicle-infrastructure/infrastructure-side/label/camera/xxxxxx.json`
* `data/DAIR-V2X-V2/cooperative-vehicle-infrastructure/infrastructure-side/label/virtuallidar/xxxxxx.json`
* `data/DAIR-V2X-V2/cooperative-vehicle-infrastructure/vehicle-side/label/camera/xxxxxx.json`
* `data/DAIR-V2X-V2/cooperative-vehicle-infrastructure/vehicle-side/label/lidar/xxxxxx.json`

### Transform point

```Python
def trans_point(input_point, translation, rotation):
    input_point = np.array(input_point).reshape(3, 1)
    translation = np.array(translation).reshape(3, 1)
    rotation = np.array(rotation).reshape(3, 3)
    output_point = np.dot(rotation, input_point).reshape(3, 1) + np.array(translation).reshape(3, 1)
    output_point = output_point.reshape(1, 3).tolist()
    return output_point[0]
```

Rotation Matrix and Translation Matrix can be obtained from the json files in the following directory:

* `data/DAIR-V2X-V2/cooperative-vehicle-infrastructure/infrastructure-side/calib/xxxx/xxxxxx.json`
* `data/DAIR-V2X-V2/cooperative-vehicle-infrastructure/vehicle-side/calib/xxxx/xxxxxx.json`

If you have the rotation matrix and translation matrix from A coordinate system to B coordinate system, you can obtain the rotation matrix and translation matrix from B coordinate system to A coordinate system through the following code:
