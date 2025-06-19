# (width, height) max values for user input image. Images too large will be shrinked
RESIZE_VALUES = (2048, 1024)

# lego object detection
ROBOFLOW_PROJECT_ID_LOD = "lego_object_detection-5lfzr"
ROBOFLOW_PROJECT_VERSION_LOD = 1
# lego brick detector
ROBOFLOW_PROJECT_ID_LBD = "lego-brick-detector-xvqkq"
ROBOFLOW_PROJECT_VERSION_LBD = 2

# Segment-anything model (SAM) hyperparameters; default and 2 relevant configs (CONFIG_1 gives best results)
SAM_DEFAULT_PARAMS = {
    "points_per_side": 32,
    "points_per_batch": 64,
    "pred_iou_thresh": 0.88,
    "stability_score_thresh": 0.95,
    "stability_score_offset": 1.0,
    "box_nms_thresh": 0.7,
    "crop_n_layers": 0,
    "crop_nms_thresh": 0.7,
    "crop_overlap_ratio": 0.34133,
    "crop_n_points_downscale_factor": 1,
    "point_grids": None,
    "min_mask_region_area": 0
}

SAM_CONFIG_1 = {
    "points_per_side": 48,
    "points_per_batch": SAM_DEFAULT_PARAMS["points_per_batch"],
    "pred_iou_thresh": 0.88,
    "stability_score_thresh": SAM_DEFAULT_PARAMS["stability_score_thresh"],
    "stability_score_offset": SAM_DEFAULT_PARAMS["stability_score_offset"],
    "box_nms_thresh": 0.7,
    "crop_n_layers": 0,
    "crop_nms_thresh": SAM_DEFAULT_PARAMS["crop_nms_thresh"],
    "crop_overlap_ratio": SAM_DEFAULT_PARAMS["crop_overlap_ratio"],
    "crop_n_points_downscale_factor": SAM_DEFAULT_PARAMS["crop_n_points_downscale_factor"],
    "point_grids": SAM_DEFAULT_PARAMS["point_grids"],
    "min_mask_region_area": 20
}

SAM_CONFIG_2 = {
    "points_per_side": 32,
    "points_per_batch": SAM_DEFAULT_PARAMS["points_per_batch"],
    "pred_iou_thresh": 0.94,
    "stability_score_thresh": SAM_DEFAULT_PARAMS["stability_score_thresh"],
    "stability_score_offset": SAM_DEFAULT_PARAMS["stability_score_offset"],
    "box_nms_thresh": 0.5,
    "crop_n_layers": 1,
    "crop_nms_thresh": SAM_DEFAULT_PARAMS["crop_nms_thresh"],
    "crop_overlap_ratio": SAM_DEFAULT_PARAMS["crop_overlap_ratio"],
    "crop_n_points_downscale_factor": SAM_DEFAULT_PARAMS["crop_n_points_downscale_factor"],
    "point_grids": SAM_DEFAULT_PARAMS["point_grids"],
    "min_mask_region_area": 20
}
