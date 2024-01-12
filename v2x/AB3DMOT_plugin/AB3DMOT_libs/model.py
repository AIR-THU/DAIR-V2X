# Author: Xinshuo Weng
# email: xinshuo.weng@gmail.com

import numpy as np, os, copy, math
from AB3DMOT_libs.box import Box3D
from AB3DMOT_libs.matching import data_association
from AB3DMOT_libs.kalman_filter import KF
from AB3DMOT_libs.vis import vis_obj
from xinshuo_miscellaneous import print_log
from xinshuo_io import mkdir_if_missing

from AB3DMOT.AB3DMOT_libs.model import AB3DMOT

np.set_printoptions(suppress=True, precision=3)


# A Baseline of 3D Multi-Object Tracking
class AB3DMOT_custom(AB3DMOT):
	def __init__(self, cfg, cat, calib=None, oxts=None, img_dir=None, vis_dir=None, hw=None, log=None, ID_init=0):
		super().__init__(cfg, cat, calib, oxts, img_dir, vis_dir, hw, log, ID_init)

	def get_param(self, cfg, cat):
		# get parameters for each dataset

		if cfg.dataset == 'KITTI':
			if cfg.det_name == 'pvrcnn':  # tuned for PV-RCNN detections
				if cat == 'Car':
					algm, metric, thres, min_hits, max_age = 'hungar', 'giou_3d', -0.2, 3, 2
				elif cat == 'Pedestrian':
					algm, metric, thres, min_hits, max_age = 'greedy', 'giou_3d', -0.4, 1, 4
				elif cat == 'Cyclist':
					algm, metric, thres, min_hits, max_age = 'hungar', 'dist_3d', 2, 3, 4
				else:
					assert False, 'error'
			elif cfg.det_name == 'pointrcnn':  # tuned for PointRCNN detections
				if cat == 'Car':
					# algm, metric, thres, min_hits, max_age = 'hungar', 'giou_3d', -0.2, 3, 2
					algm, metric, thres, min_hits, max_age = 'hungar', 'giou_3d', -0.2, 1, 21
				elif cat == 'Pedestrian':
					algm, metric, thres, min_hits, max_age = 'greedy', 'giou_3d', -0.4, 1, 4
				elif cat == 'Cyclist':
					algm, metric, thres, min_hits, max_age = 'hungar', 'dist_3d', 2, 3, 4
				else:
					assert False, 'error'
			elif cfg.det_name == 'deprecated':
				if cat == 'Car':
					algm, metric, thres, min_hits, max_age = 'hungar', 'dist_3d', 6, 3, 2
				elif cat == 'Pedestrian':
					algm, metric, thres, min_hits, max_age = 'hungar', 'dist_3d', 1, 3, 2
				elif cat == 'Cyclist':
					algm, metric, thres, min_hits, max_age = 'hungar', 'dist_3d', 6, 3, 2
				else:
					assert False, 'error'
			else:
				if cat == 'Car': 			algm, metric, thres, min_hits, max_age = 'hungar', 'giou_3d', -0.2, 3, 2
				elif cat == 'Pedestrian': 	algm, metric, thres, min_hits, max_age = 'greedy', 'giou_3d', -0.4, 1, 4 		
				elif cat == 'Cyclist': 		algm, metric, thres, min_hits, max_age = 'hungar', 'dist_3d', 2, 3, 4
				else: assert False, 'error'
		else:
			assert False, 'no such dataset'

		# add negative due to it is the cost
		if metric in ['dist_3d', 'dist_2d', 'm_dis']: thres *= -1
		self.algm, self.metric, self.thres, self.max_age, self.min_hits = \
			algm, metric, thres, max_age, min_hits

		# define max/min values for the output affinity matrix
		if self.metric in ['dist_3d', 'dist_2d', 'm_dis']:
			self.max_sim, self.min_sim = 0.0, -100.
		elif self.metric in ['iou_2d', 'iou_3d']:
			self.max_sim, self.min_sim = 1.0, 0.0
		elif self.metric in ['giou_2d', 'giou_3d']:
			self.max_sim, self.min_sim = 1.0, -1.0

	def update(self, matched, unmatched_trks, dets, info, lidar_xyzr):
		# update matched trackers with assigned detections

		dets = copy.copy(dets)
		for t, trk in enumerate(self.trackers):
			if t not in unmatched_trks:
				d = matched[np.where(matched[:, 1] == t)[0], 0]  # a list of index
				assert len(d) == 1, 'error'

				# update statistics
				trk.time_since_update = 0  # reset because just updated
				trk.hits += 1

				# update orientation in propagated tracks and detected boxes so that they are within 90 degree
				bbox3d = Box3D.bbox2array(dets[d[0]])
				trk.kf.x[3], bbox3d[3] = self.orientation_correction(trk.kf.x[3], bbox3d[3])

				if trk.id == self.debug_id:
					print('After ego-compoensation')
					print(trk.kf.x.reshape((-1)))
					print('matched measurement')
					print(bbox3d.reshape((-1)))
				# print('uncertainty')
				# print(trk.kf.P)
				# print('measurement noise')
				# print(trk.kf.R)

				# kalman filter update with observation
				trk.kf.update(bbox3d)

				if trk.id == self.debug_id:
					print('after matching')
					print(trk.kf.x.reshape((-1)))
					print('\n current velocity')
					print(trk.get_velocity())

				trk.kf.x[3] = self.within_range(trk.kf.x[3])
				trk.info = info[d, :][0]
				trk.lidar_xyzr = lidar_xyzr[d, :][0]

		# debug use only
		# else:
		# print('track ID %d is not matched' % trk.id)

	def birth(self, dets, info, unmatched_dets, lidar_xyzr):
		# create and initialise new trackers for unmatched detections

		# dets = copy.copy(dets)
		new_id_list = list()  # new ID generated for unmatched detections
		for i in unmatched_dets:  # a scalar of index
			trk = KF(Box3D.bbox2array(dets[i]), info[i, :], self.ID_count[0],lidar_xyzr[i,:])
			self.trackers.append(trk)
			new_id_list.append(trk.id)
			# print('track ID %s has been initialized due to new detection' % trk.id)

			self.ID_count[0] += 1

		return new_id_list

	def output(self):
		# output exiting tracks that have been stably associated, i.e., >= min_hits
		# and also delete tracks that have appeared for a long time, i.e., >= max_age

		num_trks = len(self.trackers)
		results = []
		for trk in reversed(self.trackers):
			# change format from [x,y,z,theta,l,w,h] to [h,w,l,x,y,z,theta]
			d = Box3D.array2bbox(trk.kf.x[:7].reshape((7,)))  # bbox location self
			d = Box3D.bbox2array_raw(d)

			if ((trk.time_since_update < 1) and (trk.hits >= self.min_hits)):
			# if ((trk.time_since_update < self.max_age) and (trk.hits >= self.min_hits or self.frame_count <= self.min_hits)):
			# if ((trk.time_since_update < self.max_age) and (trk.hits >= self.min_hits or self.frame_count <= self.min_hits)):
				results.append(np.concatenate((d, [trk.id], trk.info, trk.lidar_xyzr)).reshape(1, -1))
			num_trks -= 1

			# deadth, remove dead tracklet
			if (trk.time_since_update >= self.max_age):
				self.trackers.pop(num_trks)

		return results

	def track(self, dets_all, frame, seq_name):
		"""
		Params:
			dets_all: dict
				dets - a numpy array of detections in the format [[h,w,l,x,y,z,theta],...]
				info: a array of other info for each det
				lidar_xyzr: a array of lidar location and rotation z
			frame:    str, frame number, used to query ego pose
		Requires: this method must be called once for each frame even with empty detections.
		Returns the a similar array, where the last column is the object ID.

		NOTE: The number of objects returned may differ from the number of detections provided.
		"""
		dets, info, lidar_xyzr = dets_all['dets'], dets_all['info'], dets_all['lidar_xyzr']  # dets: N x 7, float numpy array
		if self.debug_id:
			print('\nframe is %s' % frame)

		# logging
		print_str = '\n\n*****************************************\n\nprocessing seq_name/frame %s/%d' % (seq_name, frame)
		print_log(print_str, log=self.log, display=False)
		self.frame_count += 1

		# recall the last frames of outputs for computing ID correspondences during affinity processing
		self.id_past_output = copy.copy(self.id_now_output)
		self.id_past = [trk.id for trk in self.trackers]

		# process detection format
		dets = self.process_dets(dets)

		# tracks propagation based on velocity
		trks = self.prediction()

		# ego motion compensation, adapt to the current frame of camera coordinate
		# if (frame > 0) and (self.ego_com) and (self.oxts is not None):
		# 	trks = self.ego_motion_compensation(frame, trks)

		# visualization
		# if self.vis and (self.vis_dir is not None):
		# 	img = os.path.join(self.img_dir, f'{frame:06d}.png')
		# 	save_path = os.path.join(self.vis_dir, f'{frame:06d}.jpg'); mkdir_if_missing(save_path)
		# 	self.visualization(img, dets, trks, self.calib, self.hw, save_path)

		# matching
		trk_innovation_matrix = None
		if self.metric == 'm_dis':
			trk_innovation_matrix = [trk.compute_innovation_matrix() for trk in self.trackers]
		matched, unmatched_dets, unmatched_trks, cost, affi = \
			data_association(dets, trks, self.metric, self.thres, self.algm, trk_innovation_matrix)
		# print_log('detections are', log=self.log, display=False)
		# print_log(dets, log=self.log, display=False)
		# print_log('tracklets are', log=self.log, display=False)
		# print_log(trks, log=self.log, display=False)
		# print_log('matched indexes are', log=self.log, display=False)
		# print_log(matched, log=self.log, display=False)
		# print_log('raw affinity matrix is', log=self.log, display=False)
		# print_log(affi, log=self.log, display=False)

		# update trks with matched detection measurement
		self.update(matched, unmatched_trks, dets, info, lidar_xyzr)

		# create and initialise new trackers for unmatched detections
		new_id_list = self.birth(dets, info, unmatched_dets, lidar_xyzr)

		# output existing valid tracks
		results = self.output()
		if len(results) > 0:
			results = [np.concatenate(results)]  # h,w,l,x,y,z,theta, ID, other info, confidence
		else:
			results = [np.empty((0, 19))]####ywx
		self.id_now_output = results[0][:, 7].tolist()  # only the active tracks that are outputed

		# post-processing affinity to convert to the affinity between resulting tracklets
		if self.affi_process:
			affi = self.process_affi(affi, matched, unmatched_dets, new_id_list)
		# print_log('processed affinity matrix is', log=self.log, display=False)
		# print_log(affi, log=self.log, display=False)

		# logging
		print_log('\ntop-1 cost selected', log=self.log, display=False)
		print_log(cost, log=self.log, display=False)
		for result_index in range(len(results)):
			print_log(results[result_index][:, :8], log=self.log, display=False)
			print_log('', log=self.log, display=False)

		return results, affi
