# Calibrate Camera

## Overview

This script performs camera calibration using a set of images of a checkerboard pattern. It computes the camera matrix, distortion coefficients, rotation vectors, translation vectors, and homography matrix. These parameters are essential for various computer vision tasks like 3D reconstruction, object tracking, and image perspective correction. It also contains utility function to convert undistord and warp image as well as to convert image coordinates to real world coordinates.
Usage

```bash
python calibrate_camera.py /path/to/images image_format /path/to/reference_plan.jpg square_size width height /path/to/save/calibration.yml
```

    /path/to/images: Directory containing checkerboard images.
    image_format: Format of the images (e.g., 'jpg', 'png').
    /path/to/reference_plan.jpg: Path to the reference plan image, defining the origin of the working plan.
    square_size: Size of a square on the checkerboard in real-world units (e.g., centimeters).
    width: Number of inner corners along the width of the checkerboard.
    height: Number of inner corners along the height of the checkerboard.
    /path/to/save/calibration.yml: Destination file path to save the calibration results.

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


