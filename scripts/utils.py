import os

import supervision as sv
import cv2


def show_annotated_image(img_path, pred, detections, display=True, show_labels=True, save=True, suffix="", imsize=(6,6), color=(0,0,0), thickness=4):
    """Display an image with bounding boxes and labels around detected objects.

    Inputs:
    -------
    - img_path (str)     : the path to the unannotated image
    - pred (dict)        : the "prediction" content of a JSON response dictionary. Must contain a "class" key
    - detections         : a supervision.Detections object (got with e.g. sv.Detections.from_inference(results)
    - display (bool)     : if True, plot image. Default is True
    - show_labels (bool) : if True, add labels. Default is True
    - save (bool)        : if True, save annotated image next to the original. Default is True
    - suffix (str)       : suffix to append to `img_path` (before the extension) to make the savepath.
                           Default is "_annotated". Unused if save==False
    - imsize (2-tuple)   : size of the image to display in inches. Default is (6,6)
    - color (3-tuple)    : color of the bounding boxes. Default is (0,0,0)
    - thickness (int)    : thickness of the bounding boxes. Default is 4

    Output:
    -------
    None
    """
    bounding_box_annotator = sv.BoxAnnotator(color=sv.Color(*color), thickness=thickness)

    image = cv2.imread(img_path)
    annotated_image = bounding_box_annotator.annotate(scene=image, detections=detections)
    if show_labels:
        label_annotator = sv.LabelAnnotator()
        labels = [item["class"] for item in pred]
        annotated_image = label_annotator.annotate(scene=annotated_image, detections=detections, labels=labels)

    print(f"{len(pred)} object(s) detected")
    if display:
        sv.plot_image(image=annotated_image, size=imsize)
    if save:
        if not suffix:
            suffix = "_annotated"

        dirpath, basename = os.path.split(img_path)
        filename, ext = os.path.splitext(basename)
        new_img_basename = f"{filename}{suffix}{ext}"
        savepath = os.path.join(dirpath, new_img_basename)
        cv2.imwrite(savepath, annotated_image)
        print(f"Saved annotated image to {savepath}")

    return None


def compare_predictions(pred_1, pred_2, title=""):
    """Compare predictions from 2 sources (e.g. the API call and the model.predict()).

    Inputs:
    -------
    - pred_1 (dict) : a prediction dictionary, i.e., the "prediction" key from a JSON response dictionary.
                      pred_1 should have at least key "x", "y", width", "height" and "confidence".
                      Adapt if phrasing is different.
    - pred_2 (dict) : another prediction dictionary
    - title (str)   : some text to print before the table

    Output:
    -------
    None
    """
    keys = ["x", "y", "width", "height", "confidence"]
    if len(pred_1) != len(pred_2):
        print(f"/!\\ WARNING: arg 1 has len {len(pred_1)} while arg 2 has len {len(pred_2)}. Results may be non-sense")
    if title:
        print(title)
    print("param\t API\t code\t delta\t\t rapi\t\t rcode")
    print("-"*63)
    for idx in range(min(len(pred_1), len(pred_2))):
        for k in keys:
            p1 = pred_1[idx][k]
            p2 = pred_2[idx][k]
            delta  = p1 - p2
            ratio1 = delta / p1
            ratio2 = delta / p2
            if pred_1[idx][k] < 1:  # confidence
                print(f"{k:.6s}\t {p1:.4f}\t {p2:.4f}\t {delta:+.4f}")
            else:
                print(f"{k:.6s}\t {p1:>6.1f}\t {p2:>6.1f}\t {delta:>+7.1f}\t {ratio1:>+7.3f}\t {ratio2:>+7.3f}")
        print("")

    return None
