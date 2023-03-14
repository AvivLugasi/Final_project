#!/bin/bash

###Global params###
IMAGE_NAME="image_jpeg.jpg"
ROBOFLOW_INPUT_FOLDER="roboflow_marine_debris_input"
MARINE_DEBRIS_IMAGES_INPUT_DIR="original_dataset/marine_debris_data/nasa_marine_debris_source"
MARINE_DEBRIS_LABELS_INPUT_DIR="original_dataset/marine_debris_data/nasa_marine_debris_labels"

###helper functions####
#copy marine debris image to the roboflow input dir
function cp_img(){
  folder=$1
  #extract image name
  folder_name=$(echo $folder | cut -d'/' -f4)
  # Extract image number
  prefix='nasa_marine_debris_source_'
  image_number=$(echo "$folder_name" | sed -e "s/^$prefix//")
  #copy image
  cp "$folder/$IMAGE_NAME" "$ROBOFLOW_INPUT_FOLDER/$image_number.jpg"
}

#create label file from npy file
function create_label(){
  folder=$1
  #extract image name
  folder_name=$(echo $folder | cut -d'/' -f4)
  # Extract label number
  prefix='nasa_marine_debris_labels_'
  label_number=$(echo "$folder_name" | sed -e "s/^$prefix//")
  python3 copy_img_label.py $label_number $folder
}


#create folder that will contain all the images and their labels
#mkdir $ROBOFLOW_INPUT_FOLDER

#copy all the images from the source dataset to the new directory
#for folder in "$MARINE_DEBRIS_IMAGES_INPUT_DIR"/*
#do
#    echo "copying image from folder: $folder"
#    cp_img $folder
#done

#loop labels npy files and create label files in format roboflow can get
for folder in "$MARINE_DEBRIS_LABELS_INPUT_DIR"/*
do
    echo "creating label file for: $folder"
    create_label $folder
done

