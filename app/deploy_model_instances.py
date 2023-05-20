import os
import segmentation_models as sm
import multiprocessing
import threading
import numpy as np
import tensorflow as tf
from skimage import io
from matplotlib import pyplot as plt
import cv2

os.environ["SM_FRAMEWORK"] = "tf.keras"


class ModelDeployment:
    """Create deployment of the model"""
    def __init__(self,
                 model_name: str = "efficientnetb4",
                 model_weights_path: str = "best_model_efficientnetb4_4.h5",
                 num_of_instances: int = multiprocessing.cpu_count(),
                 threshold: float = 0.8,
                 num_of_debris_pixels = 50
                 ):
        """
        Create a deployment object, which initialize 'num_of_instances' instances of the\n
        segmentation model.\n

        Args:
            model_name (str): name of the best model backbone.(default=efficientnetb4)
            model_weights_path (str): path to the folder that contain the model weights.
            num_of_instances (int): number of instances to create,<br>
                were the default is as the number of available threads.
            threshold(float): threshold for classifing pixel to either background or debris.
        """
        self.model_name = model_name
        self.model_weights_path = model_weights_path
        self.num_of_instances = num_of_instances
        self.models_list = self.create_model_instance()
        self.lock = threading.Lock()
        self.threshold = threshold
        self.num_of_debris_pixels = num_of_debris_pixels

    def create_model_instance(self):
        """
          Initialize 'num_of_instances' instances of the\n
          segmentation model.\n

          Returns:
              list with instances of the segmentation model.
        """
        models_list = []
        for i in range(self.num_of_instances):
            n_classes = 1
            activation = 'sigmoid'
            model = sm.Unet(self.model_name, classes=n_classes, activation=activation)

            dice_loss = sm.losses.DiceLoss()
            focal_loss = sm.losses.BinaryFocalLoss(gamma=2.5, alpha=0.3)
            total_loss = dice_loss + 1.5 * focal_loss

            metrics = [sm.metrics.IOUScore(threshold=0.5)]

            # compile keras model with defined optimizer, loss and metrics
            model.compile(optimizer='Adam', loss=total_loss, metrics=metrics)
            model.load_weights(self.model_weights_path)
            models_list.append(model)

        return models_list

    def pre_process(self, images):
        """
        apply pre-processing steps on the tiles.
        Args:
            images (np.ndarray(256, 256, 3)): tiles.
        Returns:
            The input arg after pre-processing.
        """
        return np.array(images)

    # helper function for data visualization
    def visualize(self, **images):
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

    def process_predictions(self, results_list: list):
        """
        plot pairs of image and its copy with contours of the predicted debris.\n

        Args:
           results_list (list): list of lists, where in each list the first element is the image<br>
                                and the second is the predicted debris in it.
        """
        for result in results_list:
            if result[2] == 1:
                file_name = os.path.basename(result[3])
                print(file_name)
                self.visualize(image=result[0], prediction=result[1])

    def draw_debris_contours(self, mask, image):
        """
        Draw contours of the predicted debris on a copy of the input image and return it.

        Args:
            mask (np.ndarray(256, 256)): predicted debris, where pixels that belong to a debris are 255,
                and the rest are 0.
            image (np.ndarray(256, 256, 3)): input tile.
        Returns:
             copy of the tile with the debris contours on it.
        """
        # Threshold the mask to create a binary image
        ret, thresh = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)
        # Convert the binary image to the CV_8UC1 format
        thresh = thresh.astype(np.uint8)
        # Find the contours of the binary image
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # Create a copy of the color image
        result = np.copy(image)
        # Draw the contours on the copy of the color image
        cv2.drawContours(result, contours, -1, (255, 0, 0), 1)
        return result

    # helper function for inference
    def predict(self, model, image) -> np.ndarray:
        """return the prediction mask on an input image.
        Args:
            model (keras.model): trained model for semantic segmentation.
            image (np.ndarray (256, 256, 3)): ndarray that represent input image.
        Returns:
            (256, 256) ndarray which represent the prediction mask.
        """
        image = np.expand_dims(image, axis=0)
        pr_mask = model.predict(image).round()
        pr_mask = np.where(pr_mask > self.threshold, 255, 0.0)
        return pr_mask[..., 0].squeeze()

    def thread_predict(self, model, images, results_list):
        """ function to run predict() and visualize() for a batch of images"""
        for image in images:
            model_input = self.pre_process(image["image"])
            prediction = self.predict(model, model_input)
            detected = 0
            # if the model predicted any debris in the image
            if len(np.unique(prediction)) == 2:
                if np.count_nonzero(prediction == 255) >= self.num_of_debris_pixels:
                    detected = 1
                    prediction = self.draw_debris_contours(mask=prediction, image=model_input)
            with self.lock:
                results_list.append([
                                    model_input,
                                    prediction,
                                    detected,
                                    image["image_path"],
                                    image["coordinates"]
                                    ])

    def execute_job(self, input_data):
        """
        predict marine debris for a list of input tiles and returns\n
        a list of lists, where in each list the first element is the image\n
        and the second is the predicted debris in it\n

        Args:
        input_data (list of np.ndarray (256, 256, 3)) : list of input tiles.
        Returns:
            list of lists, where in each list the first element is the image<br>
             and the second is the predicted debris in it
        """
        results_list = []

        # Create a list of threads to process each image
        threads = []
        # starting index of tile for a thread
        start = 0
        # the length of a batch which each thread will work on
        batch = len(input_data) // self.num_of_instances
        # the rest of the threads if there are any, for the last thread
        mod = len(input_data) % self.num_of_instances

        for i in range(self.num_of_instances):
            # if this is the last thread it might have to work on more tiles then the others
            if i < self.num_of_instances - 1:
                end = start + batch
            else:
                end = start + batch + mod

            t = threading.Thread(target=self.thread_predict,
                                 args=(self.models_list[i], input_data[start:end], results_list))
            threads.append(t)
            start += batch

        # Start all the threads
        for t in threads:
            t.start()

        # Wait for all threads to finish
        for t in threads:
            t.join()

        return results_list
