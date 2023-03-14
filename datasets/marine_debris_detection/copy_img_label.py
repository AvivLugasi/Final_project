import numpy as np
import sys

# program arguments
file_name = sys.argv[1]
path = sys.argv[2]+"/pixel_bounds.npy"

# Read an example NPZ file
x = np.load(path)

# Define the path to save the YOLO formatted labels
output_file = 'roboflow_marine_debris_input/'+file_name+'.txt'
# Define the image dimensions
image_width = 256
image_height = 256

# Open the output file for writing
with open(output_file, 'w') as f:

    # Loop through each object in the npy file
    for label in x:

        # Extract the class label and bounding box coordinates
        xmin, ymin, xmax, ymax, class_label = label

        # Convert the coordinates to YOLO format
        x_center = (xmin + xmax) / 2 / image_width
        y_center = (ymin + ymax) / 2 / image_height
        box_width = (xmax - xmin) / image_width
        box_height = (ymax - ymin) / image_height

        # Write the YOLO formatted label to the output file
        f.write(f'{class_label} {x_center:.6f} {y_center:.6f} {box_width:.6f} {box_height:.6f}\n')
