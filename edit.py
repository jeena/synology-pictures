#!/usr/bin/env python3

import cv2
import sys

def wait_with_check_closing(win_name):
    """ 
        https://stackoverflow.com/questions/35003476/"
        "opencv-python-how-to-detect-if-a-window-is-closed/37881722
    """
    while True:
        keyCode = cv2.waitKey(50)
        if keyCode != -1:
            break
        win_prop = cv2.getWindowProperty(win_name, cv2.WND_PROP_VISIBLE)
        if win_prop <= 0:
            break

class Image:
    def __init__(self, path, w=1920, h=1080):
        self.w = w
        self.h = h
        self.path = path
        self.image = cv2.imread(self.path)

    def crop(self):
        oh, ow, z = self.image.shape
        w = self.w
        h = self.h
        vertical = False
        if oh/ow < 1:
            # horizontal
            if ow <= self.w:
                w = ow
                h = oh
            else:
                # need resizing to smaller
                if self.w/ow < self.h/oh:
                    # hight priority
                    w = self.h/oh * ow
                    h = self.h
                else:
                    w = self.w
                    h = self.w/ow * oh
        else:
            # vertical
            vertical = True
            if oh <= self.h:
                w = ow
                h = oh
            else:
                # need resizing to smaller
                w = self.h/oh * ow
                h = self.h
        if vertical:
            self.image = cv2.resize(self.image, (int(w), int(h)))
            self.image = self.image[0:self.h, 0:self.w]
            bg_image = cv2.resize(self.image.copy(), (self.w, self.h))
            bg_image = cv2.blur(bg_image, (200, 200))
            x_offset = int(self.image.shape[0] / 2)
            y_offset = 0
            bg_image[y_offset:y_offset+self.image.shape[0], x_offset:x_offset+self.image.shape[1]] = self.image
            self.image = bg_image
        else:
            self.image = cv2.resize(self.image, (int(w), int(h)))
            # center zoom
            x = self.image.shape[1]/2 - self.w/2
            y = self.image.shape[0]/2 - self.h/2
            self.image = self.image[int(y):int(y+self.h), int(x):int(x+self.w)]

    def safe(self, new_path):
        cv2.imwrite(new_path, self.image)
        
    def show(self):
        title = "Image"
        cv2.imshow(title, self.image)
        wait_with_check_closing(title)
        cv2.destroyAllWindows()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: edit.py path/to/picture.jpeg")
    else:
        img_path = sys.argv[1]
        img = Image(img_path)
        img.crop()
        img.show()
        img.safe("/home/jeena/Downloads/test.jpg")
