import cv2
import os

# Tentukan directory tujuan
def addName(name):
    save_dir = "./dataset/{}".format(name)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    cam = cv2.VideoCapture(0)
    img_counter = 0
    while img_counter < 5:
        ret, frame = cam.read()
        if not ret:
            print("failed to grab frame")
            break

        cv2.imshow("Press SPACE to take a picture", frame)
        k = cv2.waitKey(1)
        if k % 256 == 32:
            # SPACE pressed
            img_name = "{}_{}.png".format(name, img_counter)
            img_path = os.path.join(save_dir, img_name)
            cv2.imwrite(img_path, frame)
            print("{} written!".format(img_path))
            img_counter += 1
    cv2.destroyAllWindows()