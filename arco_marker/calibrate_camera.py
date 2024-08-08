import numpy as np
import cv2
import glob
import csv

# Open csv file 
f = open('output/calibrate.csv', 'w', newline='')
writer = csv.writer(f)

# Set termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# Set sample image file path
path_of_images = "./test_images/"
samples = glob.glob(path_of_images + "*.jpg")

#  Number of internal corners of checkerboard (rows, columns)
checkerboard = (7, 6)

# Define object points
objp = np.zeros((checkerboard[0] * checkerboard[1], 3), np.float32)
objp[:,:2] = np.mgrid[0:checkerboard[0],0:checkerboard[1]].T.reshape(-1,2)

# Arrays to store points
points_2d = []
points_3d = []

# Set origin vector
for fname in samples:
    sample = cv2.imread(fname)                      # Read image files
    gray = cv2.cvtColor(sample, cv2.COLOR_BGR2GRAY) # Convert to grayscale
    # Finding checkerboard corners
    
    # ret -> true when desired number of corners are found in image
    ret, corners = cv2.findChessboardCorners(gray, checkerboard, None)
    
    # fine-tune the pixel coordinates -> display a checkerboard image if the desired number of corners are detected.
    if ret:
        points_3d.append(objp)
        
        # Tweaking pixel coordinates for 2D points
        corners2 = cv2.cornerSubPix(gray, corners, (11,11),(-1,-1), criteria)
        points_2d.append(corners2)
        
        # Drawing corners
        sample = cv2.drawChessboardCorners(sample, checkerboard, corners2, ret)
        cv2.imshow('img', sample)
        cv2.waitKey(50)
    
# Return known 3D point values and corresponding pixel coordinates of detected corners and calibrate camera matrix 
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(points_3d, points_2d, gray.shape[::-1], None, None)

# Closing csv file
writer.writerow(["Camera matrix"])
for i in range(0, 3):
    writer.writerow(mtx[i][:])

writer.writerow(["Camera distortion coefficients"])
writer.writerow(dist[0][:])

f.close()