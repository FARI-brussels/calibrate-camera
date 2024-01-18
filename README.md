# Calibrate Camera

## Overview

This script performs camera calibration using a set of images of a checkerboard pattern. It computes the camera matrix, distortion coefficients, rotation vectors, translation vectors, and homography matrix. These parameters are essential for various computer vision tasks like 3D reconstruction, object tracking, and image perspective correction. It also contains utility functions to undistort and warp images as well as to convert image coordinates to real-world coordinates.


## Usage

```bash
python calibrate_camera.py /path/to/images image_format /path/to/reference_plan.jpg [--square_size SQUARE_SIZE] [--width WIDTH] [--height HEIGHT] [--save_to /path/to/save/calibration.yml]

```
Parameters:

    /path/to/images: Directory containing checkerboard images.
    image_format: Format of the images (e.g., 'jpg', 'png').
    /path/to/reference_plan.jpg: Path to the reference plan image, defining the origin of the working plan.
    --square_size: (Optional) Size of a square on the checkerboard in real-world units (e.g., millimeters). Default is 25.
    --width: (Optional) Number of inner corners along the width of the checkerboard. Default is 10.
    --height: (Optional) Number of inner corners along the height of the checkerboard. Default is 7.
    --save_to: (Optional) Destination file path to save the calibration results. Default is the current directory with the filename calibration.yml.

## Examples:

Using default parameters for optional arguments:

```bash
python calibrate_camera.py /path/to/images jpg /path/to/reference_plan.jpg
```
This command will run the calibration with the default square_size (25), width (10), height (7), and save the calibration to ./calibration.yml in the current directory.

Specifying all parameters:

```bash
python calibrate_camera.py /path/to/images jpg /path/to/reference_plan.jpg --square_size 30 --width 9 --height 6 --save_to /custom/path/calibration.yml
```
This command will run the calibration with a square_size of 30 mm, width of 9, height of 6, and save the calibration to /custom/path/calibration.yml.

## Features

    Camera Calibration: Compute intrinsic parameters and distortion coefficients.
    Homography Computation: Find the transformation from image plane to world coordinates.
    Image Undistortion and Warping: Correct images for lens distortion and perspective.
    Batch Image Preprocessing: Process a batch of images for computer vision tasks.

## Dependencies

    numpy
    cv2 (OpenCV)
    glob
    matplotlib
    argparse
    os

## Main Components

    calibrate(dirpath, image_format, width, height):
        Calibrates the camera using checkerboard images.
        Outputs camera matrix, distortion coefficients, rotation and translation vectors.

    find_homography(ref_plan, mtx, dist, width, height, square_size):
        Computes the homography matrix for a reference checkerboard image.

    save_coefficients(mtx, dist, H, path) and load_coefficients(path):
        Save and load the calibration parameters to/from a file.

    undistort_image(img, mtx, dist) and warp_image(image, H, width, height):
        Apply undistortion and perspective warping to images.

    preprocess_image(img, mtx, dist, H, width, height) and batch_preprocess_images(input_folder, output_folder, calibration_path, width, height):
        Batch preprocess images for computer vision tasks.

    main():
        Entry point for the script. Parses command-line arguments and calls calibration functions.

## Example Output

    RMS re-projection error: Indicating the accuracy of calibration.
    Camera matrix and distortion coefficients.
    Rotation and translation vectors for each calibration image.


