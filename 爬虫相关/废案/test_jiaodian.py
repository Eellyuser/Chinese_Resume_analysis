# Since the execution state was reset, we need to re-import the necessary library and re-define the function for SIFT detection and matching

import cv2
import numpy as np

def detect_and_match_sift(image1, image2):
    # Initialize SIFT detector
    sift = cv2.SIFT_create()

    # Find the keypoints and descriptors with SIFT in both images
    kp1, des1 = sift.detectAndCompute(image1, None)
    kp2, des2 = sift.detectAndCompute(image2, None)

    # BFMatcher with default params
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(des1, des2, k=2)

    # Apply ratio test to find good matches
    good = []
    for m, n in matches:
        if m.distance < 0.75 * n.distance:
            good.append([m])

    return kp1, kp2, good

# Load the images again
bg_image = cv2.imread('./ip_img/target_bg.png')
icon_image = cv2.imread('./ip_img/target_icon.png')

# Convert images to grayscale
bg_gray = cv2.cvtColor(bg_image, cv2.COLOR_BGR2GRAY)
icon_gray = cv2.cvtColor(icon_image, cv2.COLOR_BGR2GRAY)

# Detect and match keypoints
kp_bg, kp_icon, good_matches = detect_and_match_sift(bg_gray, icon_gray)

# Draw matches
matched_image = cv2.drawMatchesKnn(bg_image, kp_bg, icon_image, kp_icon, good_matches, None, flags=2)

# Save and display the matched image
matched_image_path = './ip_img/sift_matched_image.png'
cv2.imwrite(matched_image_path, matched_image)

# matched_image_path, len(good_matches)  # Return the path and the number of good matches
