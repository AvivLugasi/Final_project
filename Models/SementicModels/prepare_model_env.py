import glob
import os
from abc import ABC

import numpy as np
from sklearn.model_selection import train_test_split
import tensorflow as tf
from skimage import io
from matplotlib import pyplot as plt
import albumentations as A
import cv2


# classes for data loading and preprocessing
class Dataset:
    """
    Marine debris Dataset. Read images, apply augmentation and preprocessing transformations.
    """

    def __init__(
            self,
            dataset_dir=None,
            x=None,
            y=None,
            augmentation=None,
            preprocessing=None
    ):
        """
        Marine debris Dataset. Read images, apply augmentation and preprocessing transformations.
            Args:
                dataset_dir (str): path to images, masks folder.
                x (np.ndarray (256, 256, 3)) : ndarray of the input  images.
                y (np.ndarray (256, 256)) : ndarray of the input images masks.
                augmentation (albumentations.Compose): data transformation pipeline.
                    (e.g. flip, scale, etc.)
                preprocessing (albumentations.Compose): data preprocessing
                    (e.g. normalization, shape manipulation, etc.)
        """
        if dataset_dir:
            self.x, self.y = self.load_data(dataset_dir=dataset_dir)
        else:
            self.x = x
            self.y = y

        self.augmentation = augmentation
        self.preprocessing = preprocessing

    def __getitem__(self, i: int):
        """
        Returns an augmented image and mask for specified image.
        Args:
            i (int): index of image in the dataset.
        Returns:
            image (np.ndarray (256, 256, 3)) -  augmented image mask (np.ndarray (256, 256)) - augmented image's mask
        """
        # read data
        image = np.array(self.x[i])
        mask = np.array(self.y[i])

        # apply augmentations
        if self.augmentation:
            sample = self.augmentation(image=image, mask=mask)
            image, mask = sample['image'], sample['mask']

        # apply preprocessing
        if self.preprocessing:
            sample = self.preprocessing(image=image, mask=mask)
            image, mask = sample['image'], sample['mask']

        return image, mask

    def __len__(self):
        return len(self.x)

    def load_data(self, dataset_dir):
        """
        read images and masks from the specified dir.
        Args:
            dataset_dir (str): path to the dataset directory.
        Returns:
            images (list) - list of the images as np.ndarrays labels (list) - list of the masks as np.ndarrays
        """
        images = []
        labels = []
        for filename in os.listdir(dataset_dir):
            if '.jpg' in filename:
                image_path = os.path.join(dataset_dir, filename)
                image = io.imread(image_path)
                images.append(image)
                label_path = os.path.join(dataset_dir, filename[:-4] + '.npy')
                label = np.load(label_path)
                # assert that masks contains only pixels with values of 1/0.
                label = np.where(label > 0, 1, label)
                labels.append(label)
        return images, labels

    def split_data(self) -> tuple:
        """ split data to train validation datasets, where validation size is 0.2 of the original dataset."""
        return train_test_split(self.x, self.y, test_size=0.2, random_state=42)

    def pre_process(self, x_train, y_train, x_val, y_val):
        """
        apply pre-processing steps on the images and masks.
        Args:
            x_train (np.ndarray(256, 256, 3)): train images.
            y_train (np.ndarray(256, 256)): train masks.
            x_val (np.ndarray(256, 256, 3)): validation images.
            y_val (np.ndarray(256, 256)): validation masks.
        Returns:
            The input args after pre-processing.
        """
        y_train = np.expand_dims(y_train, 3)
        y_val = np.expand_dims(y_val, 3)
        x_train = np.array(x_train)
        y_train = np.array(y_train)
        y_val = np.array(y_val)
        x_val = np.array(x_val)
        y_train = tf.cast(y_train, tf.float32)
        y_val = tf.cast(y_val, tf.float32)

        return x_train, y_train, x_val, y_val


# from tensorflow import keras
#
# Sequence = keras.utils.Sequence
import keras


class Dataloader:
    """
    Load data from dataset and form augmentation and batches.
    """

    def __init__(self, dataset, generate: int, batch_size=1, shuffle=False):
        """Load data from dataset and form augmentation and batches.

            Args:
                dataset (Dataset): instance of Dataset class for image loading and preprocessing.
                batch_size (int): Integer number of images in batch.
                generate (int): the number of augmented images, masks pairs to create from each pair from the original dataset.
                shuffle (bool): if `True` shuffle image indexes each epoch.
        """
        self.dataset = self.generate_dataset(dataset, generate)
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.indexes = np.arange(len(dataset))

    def generate_dataset(self, dataset, generate):
        """
        Create augmented dataset.
        Args:
            dataset (Dataset): instance of Dataset class for image loading and preprocessing.
            generate (int): the number of augmented images, masks pairs to create from each pair from the original dataset.
        Returns:
            dataset (Dataset) - where it's x, y values are the augmented images and their masks.
        """
        x_list = []
        y_list = []
        for i in range(len(dataset.x)):
            x_list.append(dataset.x[i])
            y_list.append(dataset.y[i])
            for augmantation_indx in range(generate):
                augmantation_image, augmantation_label = dataset[augmantation_indx]
                x_list.append(augmantation_image)
                y_list.append(augmantation_label)

        dataset.x = np.array(x_list)
        dataset.y = np.array(y_list)
        return dataset


class DataGenerator(tf.keras.utils.Sequence):
    """
       Load data from dataset and form augmentation and batches.
    """

    def __init__(self, dataset, batch_size=1, shuffle=False):
        """Load data from dataset and form augmentation and batches.

            Args:
                dataset (Dataset): instance of Dataset class for image loading and preprocessing.
                batch_size (int): Integer number of images in batch.
                shuffle (bool): if `True` shuffle image indexes each epoch.
        """
        self.dataset = dataset
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.indexes = np.arange(len(dataset))

        self.on_epoch_end()

    def __getitem__(self, i):
        """
        Create an augmented batch from specified start index.
        Args:
            i (int): starting index of sample from original dataset to create batch from.
        Returns:
            Augmented batch as np.ndarray of images masks pairs.
        """
        # collect batch data
        start = i * self.batch_size
        stop = (i + 1) * self.batch_size
        data = []
        for j in range(start, stop):
            data.append(self.dataset[j])

        # transpose list of lists
        batch = [np.stack(samples, axis=0) for samples in zip(*data)]

        return batch

    def __len__(self):
        """Denotes the number of batches per epoch"""
        return len(self.indexes) // self.batch_size

    def on_epoch_end(self):
        """Callback function to shuffle indexes each epoch"""
        if self.shuffle:
            self.indexes = np.random.permutation(self.indexes)


# ================================================================================================== #
#                                          Helper Functions                                          #
# ================================================================================================== #

# helper function for data visualization
def visualize(**images):
    """Plot images in one row."""
    n = len(images)
    plt.figure(figsize=(16, 5))
    for i, (name, image) in enumerate(images.items()):
        plt.subplot(1, n, i + 1)
        plt.xticks([])
        plt.yticks([])
        plt.title(' '.join(name.split('_')).title())
        plt.imshow(image)
    plt.show()


# helper function for data visualization
def denormalize(x):
    """Scale image to range 0..1 for correct plot"""
    x_max = np.percentile(x, 98)
    x_min = np.percentile(x, 2)
    x = (x - x_min) / (x_max - x_min)
    x = x.clip(0, 1)
    return x


# helper function for inference
def predict(model, image) -> np.ndarray:
    """return the prediction mask on an input image.
    Args:
        model (keras.model): trained model for semantic segmentation.
        image (np.ndarray (256, 256, 3)): ndarray that represent input image.
    Returns:
        (256, 256) ndarray which represent the prediction mask.
    """
    image = np.expand_dims(image, axis=0)
    pr_mask = model.predict(image).round()
    pr_mask = np.where(pr_mask > 0, 255, pr_mask)
    return pr_mask[..., 0].squeeze()


def round_clip_0_1(x, **kwargs):
    return x.round().clip(0, 1)


# define augmentations
def get_training_augmentation():
    """
    Define a set of augmentations:\n
        -HorizontalFlip\n
        -ShiftScaleRotate\n
        -RandomCrop\n
        -GaussianNoise\n
        -one of (RandomBrightness, RandomGamma, CLAHE)\n
        -one of (contract, Blur)\n
        -one of (contract, hue&Saturation values change)\n
    :return:
    """
    train_transform = [

        A.HorizontalFlip(p=0.5),

        A.ShiftScaleRotate(scale_limit=0.1, rotate_limit=45, shift_limit=0.1, p=1, border_mode=cv2.BORDER_REFLECT),

        A.PadIfNeeded(min_height=256, min_width=256, always_apply=True, border_mode=cv2.BORDER_REFLECT),

        A.RandomCrop(height=256, width=256, always_apply=True),

        A.RandomBrightness(p=0.3),

        A.Blur(blur_limit=3, p=0.5),

        A.Lambda(mask=round_clip_0_1)
    ]
    return A.Compose(train_transform)


def get_validation_augmentation():
    """Add paddings to make image shape divisible by 8"""
    test_transform = [
        A.PadIfNeeded(256, 256)
    ]
    return A.Compose(test_transform)


def get_preprocessing(preprocessing_fn):
    """Construct preprocessing transform

    Args:
        preprocessing_fn (callbale): data normalization function
            (can be specific for each pretrained neural network)
    Return:
        transform: albumentations.Compose

    """

    _transform = [
        A.Lambda(image=preprocessing_fn),
    ]
    return A.Compose(_transform)
