#!/usr/bin/python3
import os
import glob
import cv2
import numpy as np

from skimage import data
from skimage.feature import match_template



LOCAL_FOLDER_PATH       = "./pics/"
LOCAL_DECK_FOLDER_PATH  = "./deck/"
LOCAL_REF_FOLDER_PATH   = "./ref/"


# Open ref images
ref_images = [cv2.imread(file) for file in glob.glob(LOCAL_REF_FOLDER_PATH + "*.png")]
ref_names = [file for file in glob.glob(LOCAL_REF_FOLDER_PATH + "*.png")]



def compare_with_ref(card, ref):
    result = match_template(card, ref)
    ij = np.unravel_index(np.argmax(result), result.shape)
    
    if ij[1] < 80:
        highest = np.argmax(result)
    else:
        highest = 0

    return highest


def highestNumber(l):
    myMax = l[0]
    i=0
    index=0
    for num in l:
        if myMax < num:
            myMax = num
            index = i
        i+=1
    return myMax, index



def get_faction(card):

    scores = []
    i=0
    for ref in ref_images:
        #print("test with " + ref_names[i])
        scores.append( compare_with_ref(card, ref) )
        i += 1
    
    # Get lowest score = lowest differences
    result, index = highestNumber(scores)
    print("score: " + str(result))
    print("index: " + str(index))

    return ref_names[index]
    


cards = []
cards.append(cv2.imread('./pics/LCDS/LCDS1_Page_15.jpg'))                             # poseida : ange
cards.append(cv2.imread('./pics/LA VOIE/7FALLEN_CARTES_VOIE_FR_Page_012.jpg'))        # la voie : archange with atq/def = X X
cards.append(cv2.imread('./pics/LA VOIE/7FALLEN_CARTES_VOIE_FR_Page_002.jpg'))        # la voie : divinity
cards.append(cv2.imread('./pics/LCDS/LCDS3_Page_30.jpg'))                             # eondra  : golem
cards.append(cv2.imread('./pics/LCDS/LCDS_Page_28.jpg'))                              # none    : miracle


for card in cards:
    # Get faction
    height = card.shape[0]
    width = card.shape[1]
    h1 = 0
    h2 = 128
    w1 = int((width/2)-64)
    w2 = int((width/2)+64)

    faction_crop = card[h1:h2,w1:w2]
    name = get_faction(card)
    print("looks like " + name) 
    
    print("")



# DEBUG - show image
#cv2.imshow('Crop test 0', faction_crop)
#cv2.waitKey(0) # waits until a key is pressed
#cv2.destroyAllWindows() # destroys the window showing image
