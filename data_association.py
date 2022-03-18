import numpy as np
from scipy.optimize import linear_sum_assignment as linear_assignment

def iou(bb_test, bb_gt):
    '''
    Calculates the IoU between the bounding boxes from detections, trackers.
    '''
    xx1 = np.maximum(bb_test[0], bb_gt[0])
    yy1 = np.maximum(bb_test[1], bb_gt[1])
    xx2 = np.minimum(bb_test[2], bb_gt[2])
    yy2 = np.minimum(bb_test[3], bb_gt[3])
    w = np.maximum(0., xx2 - xx1)
    h = np.maximum(0., yy2 - yy1)
    wh = w * h
    iou = wh / ((bb_test[2]-bb_test[0])*(bb_test[3]-bb_test[1]) + 
                (bb_gt[2]-bb_gt[0])*(bb_gt[3]-bb_gt[1]) - wh)
    
    return iou

def associate_detections_to_trackers(detections, trackers, iou_threshold=0.3):
    '''
    Assigns detections to tracked objects (both represented as bounding boxes)
    
    Parameters
    ----------
    detections : array
        Detections of the objects in the form of [x1,y1,x2,y2].
    trackers : array
        Trakers of the objects in the form of [x1,y1,x2,y2] (if not empty).
    iou_threshold : float, optional
        Threshold IoU to assign detection to exisitng tracker. Default is 0.3.

    Returns
    -------
    Returns 3 lists of matches, unmatched_detections and unmatched_trackers.

    '''
    if(len(trackers)==0):
        return np.empty((0,2),dtype=int), np.arange(len(detections)), np.empty((0,5), dtype=int)
    
    # initialize the IoU matrix
    iou_matrix = np.zeros((len(detections), len(trackers)), dtype=np.float32)
    
    for d,det in enumerate(detections):
        for t, trk in enumerate(trackers):
            iou_matrix[d,t] = iou(det,trk)
    
    # use linear_assignment to assosiate detections with trackers considering
    # populated data in iou_matrix by maximizing the total/overall cost
    matched_indices = linear_assignment(-iou_matrix)
    
    # grab the unmatched detections
    unmatched_detections = []
    for d,det in enumerate(detections):
        if(d not in matched_indices[:,0]):
            unmatched_detections.append(d)
    
    # grab the unmatched trackers
    unmatched_trackers = []
    for t,trk in enumerate(trackers):
        if(t not in matched_indices[:,1]):
            unmatched_trackers.append(t)
    
    # filter out macthed wiht low IoU
    matches = []
    for m in matched_indices:
        if(iou_matrix[m[0],m[1]] < iou_threshold):    
            unmatched_detections.append(m[0])
            unmatched_trackers.append(m[1])  
        else:
            matches.append(m.reshape(1,2))
      
    if(len(matches)==0):
        matches = np.empty((0,2),dtype=int)
    else:
        matches = np.concatenate(matches,axis=0)      
    
    return matches, np.array(unmatched_detections), np.array(unmatched_trackers)