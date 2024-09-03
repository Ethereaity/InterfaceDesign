import json
import os
import random
import sys

import cv2
from detectron2.config import get_cfg
from detectron2.data.detection_utils import read_image
from projects.PointRend.predictor import VisualizationDemo
from point_rend import add_pointrend_config
# constants
WINDOW_NAME = "COCO detections"
import torch
import numpy as np
import time

DATASET_CATEGORIES = []
# {"name": "_background_", "id": 0, "isthing": 1, "color": [220, 20, 60]},
json_file = 'detectron/projects/PointRend/coco/annotations/train5.json'
with open(json_file, 'r') as f:
    data = json.load(f)
    for item in data['categories']:
        cate = {}
        cate["name"] = item["name"]
        cate["id"] = item["id"]
        cate["isthing"] = 1
        r, g, b = [random.randint(1, 255) for i in range(3)]
        cate["color"] = [r, g, b]
        DATASET_CATEGORIES.append(cate)
def time_sync():
    # pytorch-accurate time
    if torch.cuda.is_available():
        torch.cuda.synchronize()
    return time.time()
 
def setup_cfg():
    # load config from file and command-line arguments
    cfg = get_cfg()
    add_pointrend_config(cfg)
    cfg.merge_from_file("detectron/projects/PointRend/run/train/config.yaml")
    # Set score_threshold for builtin models
    cfg.MODEL.RETINANET.SCORE_THRESH_TEST = 0.5
    cfg.MODEL.DEVICE = 'cpu'
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5
    cfg.MODEL.WEIGHTS = "detectron/projects/PointRend/run/train/model_final.pth"#你下载的模型地址和名称mo
    cfg.freeze()
    return cfg


def get_dataset_instances_meta():
    """
    purpose: get metadata of dataset from DATASET_CATEGORIES
    return: dict[metadata]
    """
    thing_ids = [k["id"] for k in DATASET_CATEGORIES if k["isthing"] == 1]
    thing_colors = [k["color"] for k in DATASET_CATEGORIES if k["isthing"] == 1]
    # assert len(thing_ids) == 2, len(thing_ids)
    thing_dataset_id_to_contiguous_id = {k: i for i, k in enumerate(thing_ids)}
    thing_classes = [k["name"] for k in DATASET_CATEGORIES if k["isthing"] == 1]
    ret = {
        "thing_dataset_id_to_contiguous_id": thing_dataset_id_to_contiguous_id,
        "thing_classes": thing_classes,
        "thing_colors": thing_colors,
    }
    return ret

def box_iou_xyxy(box1, box2):
    # 获取box1左上角和右下角的坐标
    x1min, y1min, x1max, y1max = box1[0], box1[1], box1[2], box1[3]
    # 计算box1的面积
    s1 = (y1max - y1min + 1.) * (x1max - x1min + 1.)
    # 获取box2左上角和右下角的坐标
    x2min, y2min, x2max, y2max = box2[0], box2[1], box2[2], box2[3]
    # 计算box2的面积
    s2 = (y2max - y2min + 1.) * (x2max - x2min + 1.)

    # 计算相交矩形框的坐标
    xmin = np.maximum(x1min, x2min)
    ymin = np.maximum(y1min, y2min)
    xmax = np.minimum(x1max, x2max)
    ymax = np.minimum(y1max, y2max)
    # 计算相交矩形行的高度、宽度、面积
    inter_h = np.maximum(ymax - ymin + 1., 0.)
    inter_w = np.maximum(xmax - xmin + 1., 0.)
    intersection = inter_h * inter_w
    # 计算相并面积
    union = s1 + s2 - intersection
    # 计算交并比
    iou = intersection / union
    return iou
cfg = setup_cfg()
detectron_out = VisualizationDemo(cfg)
detectron_out.metadata = get_dataset_instances_meta()
def pointrend_detect(image_path):
    t_start = time.time()
    img = read_image(image_path, format="BGR")
    predictions, visualized_output = detectron_out.run_on_image(img)
    # out_img = visualized_output.get_image()[:, :, ::-1]
    visualized_output.save('results/pointrend_detect.jpg')
    return predictions,time.time()-t_startta

def fun(image_path):
    img = read_image(image_path, format="BGR")
    predictions, visualized_output = detectron_out.run_on_image(img)
    classes = predictions['instances']._fields['pred_classes'].tolist()
    masks = predictions['instances']._fields['pred_masks']
    pred_boxes = predictions['instances']._fields['pred_boxes'].tensor.tolist()
    return classes,masks,pred_boxes
# pointrend_detect('D:/WH Detection/test_images/IMG_20231201_151309.jpg')