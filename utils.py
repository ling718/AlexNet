#/usr/bin/python3
# -*- coding: utf-8 -*-

# library modules
import os
import pickle

from random import randint

# external library modules
from PIL import Image
import numpy as np

def img2PIL(image):
    """
    Converts an image to a pillow object.
    If it is greyscale image, then convert it to RGB first

    :param image: path to the image file
    """
    img = Image.open(image)

    if img.mode != 'RGB':
        img = img.convert('RGB')
    img.load()

    return img

def img2np(image, size=None):
    """
    Converts an image to numpy data.
    If it is greyscale image, then convert it to RGB first
    and then change to numpy array

    :param image: path to the image file
    :param size: If given reshape the image to this size.
    """
    img = Image.open(image)

    if img.mode != 'RGB':
        img = img.convert('RGB')
    if size:
        img = img.resize(size)
    img.load()

    return np.asarray(img, dtype = "int32")

def imgs2np(function):
    """
    Convert list of pillow images to its numpy equivalent.
    """

    def wrapper(*args, **kwargs):
        images = function(*args, **kwargs)

        for i, image in enumerate(images):
            images[i] = np.asarray(image, dtype=np.int32)

        return images

    return wrapper

def gen_mean_activity(base_dir):
    """
    Generate mean activity for each channel over entire training set

    :param base_dir: Base directory for training
    """
    RGB = np.zeros((3,))
    count = 0
    for folder in os.listdir(os.path.join(base_dir)):
        for image in os.listdir(os.path.join(base_dir, folder)):
            img = Image.open(os.path.join(base_dir,
                                          folder,
                                          image))
            img = resize(img)

            npimg = np.array(img)
            RGB += npimg.mean(axis=(0,1))

            count += 1

    RGB /= count

    with open('mean.pkl', 'wb') as handle:
        pickle.dump(RGB, handle, protocol=pickle.HIGHEST_PROTOCOL)

def get_mean_activity():
    """
    Get mean activity for each channel(Red, Gree, Blue)
    """
    with open('mean.pkl', 'rb') as handle:
        return pickle.load(handle)

def resize(img):
    """
    Resize the image to 256 x 256.

    Rescale the image such that the shorter side will be
    256 and then crop out the central 256 x 256 patch.
    """
    # Resize the shorter size to 256
    if img.width < 256:
        img = img.resize((256, img.height))
    if img.height < 256:
        img = img.resize((img.width, 256))

    # Find the central box
    width_mid = img.width // 2
    height_mid = img.height // 2
    left = width_mid - 128 if width_mid >= 128 else 0
    right = width_mid + 128
    upper = height_mid - 128 if height_mid >= 128 else 0
    lower = height_mid + 128

    # Crop the central 256 x 256 patch of the image
    img = img.crop((left, upper, right, lower))

    # Change the mode to RGB if it is not
    if img.mode != 'RGB':
        img = img.convert('RGB')

    return img

def preprocess(function):
    def crop(image, image_size):
        """
        Randomly crop `image_size` of the the `image`
        """
        _width, _height = (image.size[0] - image_size[0],
                           image.size[1] - image_size[1])

        start_width, start_height = (randint(0, _width),
                                     randint(0, _height))

        return image.crop((start_width, start_height,
                           start_width + image_size[0],
                           start_height + image_size[1]))

    def wrapper(*args, **kwargs):
        self = args[0]

        img = function(*args, **kwargs)
        img = resize(img)
        img = crop(img, self.image_size)
        img.load()

        npimg = np.asarray(img, dtype = "int32")
        # Subtract mean activity from each channel
        mean = get_mean_activity()

        return npimg - mean.reshape((1, 1, 3))

    return wrapper

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('image_path', metavar = 'image-path',
                        help = 'ImageNet dataset path')
    args = parser.parse_args()
    im = image2nparray(args.image_path)
    print("Without reshaping, size:", im.shape)
    im = image2nparray(args.image_path, (127, 127))
    print("After reshaping, size:", im.shape)
