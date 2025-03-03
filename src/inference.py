import cv2
import numpy as np
import argparse
import qcsnpe as qc

INPUT_WIDTH = 513
INPUT_HEIGHT = 513
CPU = 0
GPU = 1
DSP = 2
model_path = "/data/model/deeplabv3_plus_mobilenet_quantized.dlc"
out_layers = []
model = qc.qcsnpe(model_path, out_layers, DSP)

# Example segmentation colors (expand as needed)
segmentation_colors = np.array([
    [0, 0, 0],       # Class 0
    [34, 139, 34],   # Class 1
    [0, 0, 255],     # Class 2
    # Add more colors for other classes
], dtype=np.uint8)

def prepare_input(image):
    img_height, img_width = image.shape[:2]
    input_img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    input_img = cv2.resize(input_img, (INPUT_WIDTH, INPUT_HEIGHT))
    return input_img

def draw_seg(seg_map, image, alpha=0.3):
    color_segmap = cv2.resize(image, (seg_map.shape[1], seg_map.shape[0]))
    mask = seg_map > 0
    color_segmap[mask] = segmentation_colors[seg_map[mask] % len(segmentation_colors)]
    color_segmap = cv2.resize(color_segmap, (image.shape[1], image.shape[0]))
    if alpha == 0:
        combined_img = np.hstack((image, color_segmap))
    else:
        combined_img = cv2.addWeighted(image, alpha, color_segmap, (1 - alpha), 0)
    return combined_img

def hybridnet(image_path):
    try:
        frame = cv2.imread(image_path)
        if frame is None:
            print("Error: Could not read the image.")
            return
        new_frame = prepare_input(frame)
        out = model.predict(new_frame)
        seg_map = out.get("output_0")
        if seg_map is None:
            print("Error: Segmentation map not found in output.")
            return
        seg_map = np.array(seg_map)
        print(f"Raw segmentation map shape: {seg_map.shape}")
        
        # Assume the output needs to be reshaped based on some expected dimensions
        expected_shape = (INPUT_HEIGHT, INPUT_WIDTH, 21)  # Example expected shape
        total_elements = np.prod(expected_shape)
        if seg_map.size != total_elements:
            print("Error: Unexpected size of segmentation map.")
            return
        
        seg_map = seg_map.reshape(expected_shape)
        seg_map = np.squeeze(np.argmax(seg_map, axis=2))
        seg_img = draw_seg(seg_map, frame, 0.3)
        cv2.imwrite("Segmentation_Output_DSP.jpg", seg_img)
    except Exception as e:
        print("Error occurred: {}".format(e))

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", required=True, help="path to input image")
    args = vars(ap.parse_args())
    image_path = args["image"]
    hybridnet(image_path)

