#!/usr/bin/env python3

import cv2
import sys
import numpy as np
import exif
from geopy.geocoders import Nominatim
from datetime import datetime
import pathlib
import os

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

def dms_coordinates_to_dd_coordinates(coordinates, coordinates_ref):
    decimal_degrees = coordinates[0] + \
                      coordinates[1] / 60 + \
                      coordinates[2] / 3600
    if coordinates_ref == "S" or coordinates_ref == "W":
        decimal_degrees = -decimal_degrees
    return decimal_degrees

class Image:
    def __init__(self, path, w=3840, h=2160):
        print("editing", path)
        self.w = w
        self.h = h
        self.path = path
        self.image = cv2.imread(self.path)
        self.geolocator = Nominatim(user_agent="jeena-synology-pictures")

    def get_exif(self):
        with open(self.path, 'rb') as img:
            e = exif.Image(img)
        if e and e.has_exif:
            return e
        else:
            return None

    def get_place_name(self, e):
        elat = e.get('gps_latitude', None)
        elng = e.get('gps_longitude', None)
        if elat and elng:
            lat = str(dms_coordinates_to_dd_coordinates(elat, e['gps_latitude_ref']))
            lng = str(dms_coordinates_to_dd_coordinates(elng, e['gps_longitude_ref']))
            location = self.geolocator.reverse(lat + ", " + lng, language="en")
            if location:
                city = location.raw.get('address', {}).get('city', None)
                country = location.raw.get('address', {}).get('country', None)
                name = ", ".join(list(filter(lambda x: x, [city, country])))
                if name != "":
                    return name
        return None
        
    def get_takentime(self):
        e = self.get_exif()
        date = None
        if e == None:
            date = os.path.basename(self.path)
        if date == None:
            date = e.get('datetime_original')
        if date == None:
            date = e.get('datetime')
        if date == None:
            date = e.get('datetime_digitized')
        if date == None:
            date = e.get('gps_datestamp')
        if date == None:
            date = os.path.basename(self.path)
        return date

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
            x_offset = int(self.w / 2 - self.image.shape[1] / 2)
            y_offset = int(self.h / 2 - self.image.shape[0] / 2)
            bg_image = self.blurry_bg(self.image)
            bg_image[y_offset:y_offset+self.image.shape[0], x_offset:x_offset+self.image.shape[1]] = self.image
            self.image = bg_image
        else:
            self.image = cv2.resize(self.image, (int(w), int(h)))
            # center zoom
            x = self.image.shape[1]/2 - self.w/2
            y = self.image.shape[0]/2 - self.h/2
            print (x,y)
            if x >= 0 and y >= 0:
                self.image = self.image[int(y):int(y+self.h), int(x):int(x+self.w)]
            else:
                self.image = self.image[0:self.h, 0:self.w]
                bg_image = self.blurry_bg(self.image)
                x_offset = int(self.w / 2 - self.image.shape[1] / 2)
                y_offset = int(self.h / 2 - self.image.shape[0] / 2)
                bg_image[y_offset:y_offset+self.image.shape[0], x_offset:x_offset+self.image.shape[1]] = self.image
                self.image = bg_image          
                
    def blurry_bg(self, image):
        bg_image = cv2.resize(image.copy(), (self.w, self.h))
        # make darker 
        bg_image = cv2.add(bg_image, np.array([-25.0]))
        bg_image = cv2.blur(bg_image, (200, 200))
        return bg_image
            
    
    def add_metadata(self):
        e = self.get_exif()
        if e:
            line = 1
            dt = e.get('datetime_original', e.get('datetime', None))
            place = self.get_place_name(e)
            if place:
                self.writeText(place, line)
                line += 1
            if dt:
                d = datetime.strptime(dt, "%Y:%m:%d %H:%M:%S")
                date = d.strftime("%Y-%m-%d %H:%M")
                self.writeText(date, line)
                line += 1


    def writeText(self, text, line_from_bottom):
        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_size = 1
        font_color = BLACK
        font_thickness = 4
        line_height = 1.2
        padding = 50
        textsize, baseline = cv2.getTextSize(text, font, font_size, font_thickness)
        x = self.image.shape[1] - textsize[0] - padding
        y = int(self.image.shape[0] - textsize[1] * line_from_bottom * line_height + baseline - padding)
        # outline
        self.image = cv2.putText(self.image,
                                 text,
                                 (x,y),
                                 font,
                                 font_size,
                                 font_color,
                                 font_thickness,
                                 cv2.LINE_AA)
        # text
        font_color = WHITE
        font_thickness = 2
        self.image = cv2.putText(self.image,
                                 text,
                                 (x,y),
                                 font,
                                 font_size,
                                 font_color,
                                 font_thickness,
                                 cv2.LINE_AA)
        

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
        img.get_takentime()
        img.crop()
        img.add_metadata()
        #img.show()
        img.safe("/home/jeena/Downloads/test.jpg")
