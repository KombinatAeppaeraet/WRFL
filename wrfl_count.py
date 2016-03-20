import cv2
import numpy as np
import sys
import re
import glob

'''
    checks current image.
    290 template images are used to find nest match

    to be included from wrfl.py
'''



class switch(object):
    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):
        """Return the match method once, then stop"""
        yield self.match
        raise StopIteration

    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if self.fall or not args:
            return True
        elif self.value in args: # changed for v1.5, see below
            self.fall = True
            return True
        else:
            return False


def loadImage(path, name, S, gray):

    # Load color image
    fname = path + name
    if gray:
        img = cv2.imread(fname, cv2.IMREAD_GRAYSCALE)
    else:
        img = cv2.imread(fname, cv2.IMREAD_COLOR)
    

    if S != 1:
        img_width = np.size(img, 0)
        img_height = np.size(img, 1)

        # change size:
        sz = (int(round(S*img_width)), int(round(S*img_height)))
        img2 = cv2.resize(img, dsize=sz)
        img = img2

    return img


'''
def loadImage(path, name, S, gray):

    # Load color image
    fname = path + name
    img = cv2.imread(fname, cv2.IMREAD_COLOR)

    # make it gray
    if gray:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    if S != 1:
        img_width = np.size(img, 0)
        img_height = np.size(img, 1)

        # change size:
        sz = (int(round(S*img_width)), int(round(S*img_height)))
        img2 = cv2.resize(img, dsize=sz)
        img = img2

    return img
'''

def loadTemplates(gray):
    pattern = re.compile("^/opt/wrfl/templates/([1-6])\.([0-9]+)\.png$")

    all = [[],[],[],[],[],[]]
    for fn in glob.glob("/opt/wrfl/templates/*.png"):
        if pattern.match(fn):
            aha = re.search(pattern, fn)
            pip = int(aha.group(1)) - 1
            idx = int(aha.group(2))
            all[pip].append(loadImage('', fn, 1, gray))

    return all


# all templates
def matchAllTemplates(T, img, method, threshold, useMaximum):
    best_idx = -1
    best_n = 0
    best_timp = 0

    nn = [0,0,0,0,0,0]

    w = np.size(T[5][1], 0)
    h = np.size(T[5][1], 1)

    idx = 0
    for pip in T:

        # N = 0
        for timp in pip:

            N = 0

            res = cv2.matchTemplate(img, timp, method)

            if useMaximum:
                loc = np.where( res >= threshold)
            else:
                loc = np.where( res <= threshold)

            for pt in zip(*loc[::-1]):
                N += 1
                nn[idx] += 1

            if N > best_n:
                best_n = N
                best_idx = idx
                best_timp = timp

        idx += 1

    return best_idx + 1

def getMethod():

    threshold = 0.5

    what = 2        ## YESS !!
    for case in switch(what):
        if case(1):
            return cv2.TM_CCOEFF, threshold, True

        if case(2):
            return cv2.TM_CCOEFF_NORMED, threshold, True

        if case(3):
            return cv2.TM_CCORR, threshold, True

        if case(4):
            return cv2.TM_CCORR_NORMED, threshold, True

        if case(5):
            return cv2.TM_SQDIFF, threshold, False

        if case(6):
            return cv2.TM_SQDIFF_NORMED, threshold, False

        if case(): # default, could also just omit condition or 'if True'
            print "oops!"



def countPip():

    # gray is ok, should be faster
    gray = True

    # load all template images
    T = loadTemplates(gray)

    method, threshold, useMaximum = getMethod()

    # img = loadImage('img/', 'w.jpg', 1, gray)
    img = loadImage('', '/opt/wrfl/img/w.jpg', 1, gray)

    # testing against all templates
    pips = matchAllTemplates(T, img, method, threshold, useMaximum)
    if pips > 0:
        return pips
    else:
        return 0





