"""
use it like 
python calibrate_camera.py /home/fari/Pictures/calibrationcheckerboard/calibration jpg /home/fari/Pictures/calibrationcheckerboard/ref_plan.jpg 25 10 7 ./calibration.yml 
"""
import argparse
import numpy as np
import cv2
import glob
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import os

# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

def calibrate(dirpath, image_format, width, height):
    """
    Apply camera calibration operation for images in the given directory path.
    
    Parameters:
    - dirpath (str): The path to the directory containing the images.
    - image_format (str): The format of the images (e.g., 'png' or 'jpg').
    - square_size (float): Size of a square on the chessboard in real-world units (e.g., centimeters).
    - ref_plan_path (str): Path to the reference plan image.
    - width (int): Number of inner corners of the chessboard along its width.
    - height (int): Number of inner corners of the chessboard along its height.
    
    Returns:
    - ret (float): Root mean square (RMS) re-projection error.
    - mtx (numpy.ndarray): Camera matrix (intrinsic parameters).
    - dist (numpy.ndarray): Distortion coefficients.
    - rvecs (list of numpy.ndarray): Rotation vectors for each image used in calibration.
    - tvecs (list of numpy.ndarray): Translation vectors for each image used in calibration.
    """
    
    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(8,6,0)
    objp = np.zeros((height*width, 3), np.float32)
    objp[:, :2] = np.mgrid[0:width, 0:height].T.reshape(-1, 2)
    objp = objp 

    # Arrays to store object points and image points from all the images.
    objpoints = []  # 3d point in real world space
    imgpoints = []  # 2d points in image plane.

    if dirpath[-1:] == '/':
        dirpath = dirpath[:-1]

    images = glob.glob(dirpath+'/' + '*.' + image_format)
    for fname in images:
        img = cv2.imread(fname)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Find the chess board corners
        ret, corners = cv2.findChessboardCorners(gray, (width, height), None)

        # If found, add object points, image points (after refining them)
        if ret:
            objpoints.append(objp)
            corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            imgpoints.append(corners2)

            # Draw and display the corners
            img = cv2.drawChessboardCorners(img, (width, height), corners2, ret)

    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
    
    return ret, mtx, dist, rvecs, tvecs


def find_homography_from_checkerboad(ref_plan, mtx, dist, width, height, square_size):
    """
    Find the homography matrix for a given reference checkerboard image.
    
    Parameters:
    - ref_plan (str or numpy.ndarray): Path to the reference checkerboard image or the image itself.
    - width (int): Number of inner corners of the checkerboard along its width.
    - height (int): Number of inner corners of the checkerboard along its height.
    
    Returns:
    - homography (numpy.ndarray): Homography matrix.
    - status (numpy.ndarray): Status of matched points (1 = valid point, 0 = invalid point).
    """
    
    # If the input is a string (path), read the image
    if isinstance(ref_plan, str):
        ref_plan = cv2.imread(ref_plan)
    ref_plan = undistort_image(ref_plan, mtx, dist)
    gray = cv2.cvtColor(ref_plan, cv2.COLOR_BGR2GRAY)
    ret, corners = cv2.findChessboardCorners(gray, (width, height), None)
    
    if not ret:
        raise ValueError("Checkerboard not found in the provided image.")
    
    # Define the points for the perfect grid in standard coordinates
    objp = np.zeros((height*width, 2), np.float32)
    objp[:, :2] = np.mgrid[0:width, 0:height].T.reshape(-1, 2)*square_size
    # Translate the object points by (25, 25) to shift the origin to the upper right corner of the calibration checkerboard 
    objp += np.array([25, 25], dtype=np.float32)
    # Compute the homography matrix
    homography, status = cv2.findHomography(corners, objp)
    
    return homography, status


def save_coefficients(mtx, dist, H, path):
    """ Save the camera matrix, distortion coefficients and perspective matrix to given path/file. """
    cv_file = cv2.FileStorage(path, cv2.FILE_STORAGE_WRITE)
    cv_file.write("K", mtx)
    cv_file.write("D", dist)
    cv_file.write("H", H)
    cv_file.release()

def load_coefficients(path):
    """
    Load camera matrix (K) and distortion coefficients (D) from a file.

    Parameters:
    - path (str): Path to the file containing camera calibration coefficients.

    Returns:
    - mtx (numpy.ndarray): Camera matrix (intrinsic parameters).
    - dist (numpy.ndarray): Distortion coefficients.
    """
    cv_file = cv2.FileStorage(path, cv2.FILE_STORAGE_READ)
    mtx = cv_file.getNode("K").mat()
    dist = cv_file.getNode("D").mat()
    H = cv_file.getNode("H").mat()
    cv_file.release()
    
    return mtx, dist, H


def undistort_image(img, mtx, dist):
    """
    Load the coefficients, undistort and warp the input image.
    
    Parameters:
    - img_path: Path to the image to be undistorted and warped.
    - calibration_file: Path to the YML file with calibration matrices.
    
    Returns:
    - undistorted_img: Undistorted image.
    """
    undistorted_img = cv2.undistort(img, mtx, dist)
    return undistorted_img


def point_coordinates_to_world_coordinates(img_point, H):
    """
    Transform a point from image coordinates to world coordinates using a given homography matrix.
    
    Parameters:
    - img_point (list or tuple): Image point in the format [x, y].
    - H (numpy.ndarray): Homography matrix.
    
    Returns:
    - world_point (list): Transformed point in world coordinates in the format [X, Y].
    """
    # Convert point to homogeneous coordinates
    img_point_homogeneous = np.array([img_point[0], img_point[1], 1])
    
    # Use the homography matrix to get world coordinates in homogeneous form
    world_point_homogeneous = np.dot(H, img_point_homogeneous)
    
    # Convert back from homogeneous coordinates to 2D
    world_point = world_point_homogeneous[:2] / world_point_homogeneous[2]
    
    return world_point.tolist()



def generate_aruco_markers(num_markers=4, marker_size=100):
    # Get the ArUco dictionary
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    
    for i in range(num_markers):
        # Generate the marker
        img = cv2.aruco.generateImageMarker(aruco_dict, i, marker_size)
        cv2.imwrite(f'aruco_marker_{i}.jpg', img)


def detect_aruco_corners(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    parameters = cv2.aruco.DetectorParameters_create()
    corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
    
    top_left_corners = [c[0][0] for c in corners] # Extracting the top-left corner of each marker
    return top_left_corners, ids

def find_homography_from_aruco(image_path, real_world_positions):
    top_left_corners, _ = detect_aruco_corners(image_path)
    if len(top_left_corners) < 4:
        raise ValueError("Less than 4 ArUco markers detected.")
    
    # Assuming real_world_positions is a list of 4 points in the format [(x1, y1), (x2, y2), ..., (x4, y4)]
    pts_src = np.array(top_left_corners, dtype=np.float32)
    pts_dst = np.array(real_world_positions, dtype=np.float32)
    
    # Calculate the Homography matrix
    H, status = cv2.findHomography(pts_src, pts_dst)
    return H


def warp_image(image, H, width, height):
    # Display image as if the camera was directly above the working plan (bird's eye view)
    
    
    # Warp the source image
    corrected_image = cv2.warpPerspective(image, H, (width, height))
    
    # Display the original and corrected images
    return corrected_image


def preprocess_image(img, mtx, dist, H,  width=640, height=480):
    if isinstance(img, str):
        img = cv2.imread(img)
    undistorted_image= undistort_image(img, mtx, dist)
    warped_image= warp_image(undistorted_image, H, width, height)
    return warped_image


def batch_preprocess_images(input_folder, output_folder, calibration_path, width=640, height=480):
    mtx, dist, H = load_coefficients(calibration_path)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
            image_path = os.path.join(input_folder, filename)
            preprocessed_image = preprocess_image(image_path, mtx, dist, H, width, height)
            output_path = os.path.join(output_folder, filename)
            cv2.imwrite(output_path, preprocessed_image)
            print(f'Processed image saved to {output_path}')

def main():
    parser = argparse.ArgumentParser(description='Camera Calibration')
    parser.add_argument('dirpath', type=str, help='Path to the directory containing the images')
    parser.add_argument('image_format', type=str, help='Image format (e.g., "png" or "jpg")')
    parser.add_argument("ref_plan_path", type=str, help='path to the reference plan that gives the origin of the working plan. The origin is the upper left corner')
    parser.add_argument('--square_size', type=float, default=25, help='Size of an edge of the square of the checkerboard in millimeters')
    parser.add_argument('--width', type=int, default=10, help='Number of inner corners along the width')
    parser.add_argument('--height', type=int, default=7, help='Number of inner corners along the height')
    parser.add_argument('--save_to', type=str, default='./calibration.yml', help='Path to where to save the calibration')

    args = parser.parse_args()

    args = parser.parse_args()

    dirpath = args.dirpath
    image_format = args.image_format
    width = args.width
    height = args.height
    path = args.save_to
    ref_plan_path = args.ref_plan_path 
    square_size = args.square_size

    ret, mtx, dist, rvecs, tvecs = calibrate(dirpath, image_format, width, height)
    H, _ = find_homography_from_checkerboad(ref_plan_path, mtx, dist, width, height, square_size)
    save_coefficients(mtx, dist, H, path)
    print(f"RMS re-projection error: {ret}")
    print("Camera matrix (intrinsic parameters):")
    print(mtx)
    print("Distortion coefficients:")
    print(dist)
    print("Rotation vectors for each image used in calibration:")
    print(rvecs)
    print("Translation vectors for each image used in calibration:")
    print(tvecs)

if __name__ == '__main__':
    m = detect_aruco_corners('/home/fari/Pictures/calibrationcheckerboard/calibration/IMG_20210614_155153.jpg')
    #main()