#!/usr/bin/python3
import os
import glob
import cv2
import math
import base64
import numpy as np
import mysql.connector
from past.builtins import execfile

# will convert the image to text string
import pytesseract



print('--- MYSQL CONNECTION TEST START ---')
execfile('mysql_co.py')
print(mydb)

db_cursor = mydb.cursor()
db_cursor.execute("SHOW DATABASES")
for db in db_cursor:
	print(db)
print('--- MYSQL CONNECTION TEST STOP ---\n')

MYSQL_TARGET_TABLE = "ALL_CARDS"


LOCAL_FOLDER_PATH       = "./pics/"
LOCAL_DECK_FOLDER_PATH  = "./deck/"
LOCAL_REF_FOLDER_PATH   = "./ref/"


cards = []

cards_lcds = [cv2.imread(file) for file in glob.glob("./pics/LCDS/*.png")]
cards_lcds += [cv2.imread(file) for file in glob.glob("./pics/LCDS/*.jpg")]

cards_tdll = [cv2.imread(file) for file in glob.glob("./pics/TDLL/*.png")]
cards_tdll += [cv2.imread(file) for file in glob.glob("./pics/TDLL/*.jpg")]

cards_pc1 = [cv2.imread(file) for file in glob.glob("./pics/Purete_celeste/*.png")]
cards_pc1 += [cv2.imread(file) for file in glob.glob("./pics/Purete_celeste/*.jpg")]

cards_lv1 = [cv2.imread(file) for file in glob.glob("./pics/LA VOIE/*.png")]
cards_lv1 += [cv2.imread(file) for file in glob.glob("./pics/LA VOIE/*.jpg")]

# TDLL TEST
#cards = [cv2.imread(file) for file in glob.glob("./pics/*/*.png")]
#cards += [cv2.imread(file) for file in glob.glob("./pics/*/*.jpg")]

#cards = [cv2.imread(file) for file in glob.glob("./*.png")]

#cards.append(cv2.imread('./pics/TDLL/TDLL_016.png'))                                # TDLL    : ange
#cards.append(cv2.imread('./pics/LCDS/LCDS1_Page_15.jpg'))                           # poseida : archange
#cards.append(cv2.imread('./pics/LA VOIE/7FALLEN_CARTES_VOIE_FR_Page_012.jpg'))      # la voie : archange with atq/def = X X
#cards.append(cv2.imread('./pics/LA VOIE/7FALLEN_CARTES_VOIE_FR_Page_002.jpg'))      # la voie : divinity
#cards.append(cv2.imread('./pics/LA VOIE/7FALLEN_CARTES_VOIE_FR_Page_005.jpg'))      # la voie : divinity
#cards.append(cv2.imread('./pics/LCDS/LCDS3_Page_30.jpg'))                           # eondra  : golem
#cards.append(cv2.imread('./pics/LCDS/LCDS_Page_28.jpg'))                            # none    : miracle
#cards.append(cv2.imread('./pics/TDLL/TDLL_019.png'))                                # TDLL    : ange
#cards.append(cv2.imread('./pics/TDLL/eleveuse de dragon.png'))                      # EONDRA  : ange
#cards.append(cv2.imread('./pics/TDLL/TDLL_045.png'))                                # MECA    : ange
#cards.append(cv2.imread('./pics/TDLL/TDLLB_Page_62.png'))                           # CEL     : ange
#cards.append(cv2.imread('./pics/TDLL/TDLL_obscura.png'))                            # NSF     : ange


def is_similar(image1, image2):
    return image1.shape == image2.shape and not(np.bitwise_xor(image1,image2).any())


card_ok=0;
all_card=0;
i=0
ext_string = "LV"
for card in cards_lv1:    

    height = card.shape[0]
    width = card.shape[1]

    # Recreate the same file
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
    encimg = cv2.imencode('.jpg', card, encode_param)[1].tobytes()
    
    nparrl = np.frombuffer(encimg, np.uint8)
    local_img = cv2.imdecode(nparrl, cv2.IMREAD_COLOR)

    # Search for the same occurence in database
    #print("Search for card number " + str(i))
    
    # Find card
    card_is_found=0
    sql_query = "select cle,carte FROM `ALL_CARDS`"
    db_cursor.execute(sql_query)
    record = db_cursor.fetchall()
    for row in record:
        cle = row[0]
        ddb_img_bytes = row[1]

        nparr = np.frombuffer(ddb_img_bytes, np.uint8)
        ddb_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if is_similar(local_img, ddb_img):
            # WE FOUND IT
            card_is_found=1
            break

    if card_is_found == 1:
        """
        print("OK, cle is " + str(cle));
        print("Will add: ")
        print(*capa_filtered, sep=' ')
        card_ok += 1
        """
        sql = "UPDATE `ALL_CARDS` SET `Extension`='"+ext_string+"' WHERE `cle`="+str(cle)
        print("REQUEST= " + sql)
        db_cursor.execute(sql)
        mydb.commit()


    #cv2.imwrite("./edited_image" + str(i) + ".png", card)
    i+=1
    all_card += 1
    
    #if i==20:
    #    break
    
    #print("---")

print("All card = " + str(all_card));
print("Probably found = " + str(card_ok));

