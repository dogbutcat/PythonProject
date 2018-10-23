import cv2
import os


def read_image(file_path):
    image_data = cv2.cv2.imread(file_path)
    print(type(image_data))


def write_image(data):
    cv2.cv2.imwrite()


if __name__ == '__main__':
    file_path = os.path.join(
        os.path.split(os.path.realpath(__file__))[0], '83.jpeg')
    read_image(file_path)
