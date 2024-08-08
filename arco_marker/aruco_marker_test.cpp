#include <opencv2/videoio.hpp>
#include <opencv2/highgui.hpp>
#include <opencv2/aruco.hpp>
#include <opencv2/calib3d.hpp>
#include <iostream>

int main() {
    // Variables for video function
    cv::VideoCapture video(cv::CAP_DSHOW);
    float markerLength = 0.05;

    float camera_matrix[3][3] = {{1209.642391, 0, 935.7920144},
                                {0, 1204.983532, 483.6240085},
                                {0, 0, 1}
                                };
    cv::Mat cameraMatrix = cv::Mat(3, 3, CV_32F, camera_matrix);
    float dist_coeffs[5] = {0.07497212, -0.10657644, -0.01026882, -0.008200681, -0.077324179};
    cv::Mat distCoeffs = cv::Mat(1, 5, CV_32F, dist_coeffs);

    cv::aruco::DetectorParameters detectorParams = cv::aruco::DetectorParameters();
    cv::aruco::Dictionary dictionary = cv::aruco::getPredefinedDictionary(cv::aruco::DICT_4X4_250);
    cv::aruco::ArucoDetector detector(dictionary, detectorParams);

    // Set coordinate system
    cv::Mat objPoints(4, 1, CV_32FC3);
    objPoints.ptr<cv::Vec3f>(0)[0] = cv::Vec3f(-markerLength/2.f, markerLength/2.f, 0);
    objPoints.ptr<cv::Vec3f>(0)[1] = cv::Vec3f(markerLength/2.f, markerLength/2.f, 0);
    objPoints.ptr<cv::Vec3f>(0)[2] = cv::Vec3f(markerLength/2.f, -markerLength/2.f, 0);
    objPoints.ptr<cv::Vec3f>(0)[3] = cv::Vec3f(-markerLength/2.f, -markerLength/2.f, 0);

    if (!video.isOpened()) {
        std::cout << "The camera does't work!" << std::endl;
        return -1;
    }

    while (video.grab()) {
        cv::Mat image, imageCopy;
        video.retrieve(image);
        image.copyTo(imageCopy);
        
        std::vector<int> ids;
        std::vector<std::vector<cv::Point2f>> corners;
        detector.detectMarkers(image, corners, ids);
        
        if (ids.size() > 0) {
            cv::aruco::drawDetectedMarkers(imageCopy, corners, ids);

            int nMarkers = corners.size();
            std::vector<cv::Vec3d> rvecs(nMarkers), tvecs(nMarkers);
            // Calculate pose for each marker
            for (int i = 0; i < nMarkers; i++) {
                solvePnP(objPoints, corners.at(i), cameraMatrix, distCoeffs, rvecs.at(i), tvecs.at(i));
            }

            // Draw axis for each marker
            for(unsigned int i = 0; i < ids.size(); i++) {
                cv::drawFrameAxes(imageCopy, cameraMatrix, distCoeffs, rvecs[i], tvecs[i], 0.1);
            }
        }

        cv::imshow("out", imageCopy);
        char key = (char) cv::waitKey(10);
        if (key == 27)
            break;
    }
    return 0;
}