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


ALL_CAPA_LIST = [
'Assassin',
'Berserk',
'Catalyseur',
'Collatéral',
'Doppelgänger',
'Egide',
'Flamme',
'Fourberie',
'Gardien',
'Geler',
'Intervention Divine',
'Lumière',
'Mort Subite',
'Pacifiste',
'Phoenix',
'Retrait',
'Symbiose',
'Tempête',
'Trésor',
'Valhalla',
'Archerie',
'Damné',
'Esquive',
'Honneur',
'Invocation',
'Sacrifice',
'Vaillant']



cards = []

cards = [cv2.imread(file) for file in glob.glob("./pics/*/*.png")]
cards += [cv2.imread(file) for file in glob.glob("./pics/*/*.jpg")]

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


# get grayscale image
def get_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

#template matching
def match_template(image, template):
    return cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED) 


def read_name(card):
    height = card.shape[0]
    width = card.shape[1]

    
    if math.floor(width/10) == math.floor(height/10):
        # Jeton
        h1 = 15
        h2 = 32
        w1 = 160
        w2 = width-160
    elif height > width:
        # normal card
        h1 = height-52
        h2 = height-27
        w1 = 80
        w2 = width-80
    else:
        # divinity
        h1 = height-40
        h2 = height-20
        w1 = 80
        w2 = int((width/2)-25)

    bot_crop = card[h1:h2,w1:w2]

    gray = get_grayscale(bot_crop)
    selected_image = gray

    # converts the image to result and saves it into result variable
    custom_config = r"-l fra --psm 6 -c tessedit_char_whitelist=' ABCDEFGHIJKLMNOPQRSTUVWXYZÀÉÈÊ'"
    result = pytesseract.image_to_string(selected_image, config=custom_config)
    
    #cv2.imwrite("./image_" + str(i) + "_name.png", selected_image)
    
    return result.strip()



def read_capa(card):
    height = card.shape[0]
    width = card.shape[1]

    
    if math.floor(width/10) != math.floor(height/10) and height > width:
        # divinity
        h1 = height-195
        h2 = height-175
        w1 = 20
        w2 = width-20

        bot_crop = card[h1:h2,w1:w2]

        gray = get_grayscale(bot_crop)
        selected_image = cv2.bitwise_not(gray)

        # converts the image to result and saves it into result variable
        custom_config = r"-l fra --psm 6 -c tessedit_char_whitelist=' abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZéèàêÀÉÈÊ()|/\+-X0123456789'"
        result = pytesseract.image_to_string(selected_image, config=custom_config)
        
        #print(result)
        #cv2.imwrite("./image_" + str(i) + "_name.png", selected_image)
    
        return result.strip()
    return ""


def is_similar(image1, image2):
    return image1.shape == image2.shape and not(np.bitwise_xor(image1,image2).any())


card_ok=0;
all_card=0;
i=0
for card in cards:    

    height = card.shape[0]
    width = card.shape[1]
    capa = read_capa(card)
    
    # Get all recognized capa
    capa_filtered = [x for x in ALL_CAPA_LIST if x in capa]
    
    #print("CAPA: " + capa)
    
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

    if card_is_found == 1 and len(capa_filtered) > 0:
        """
        print("OK, cle is " + str(cle));
        print("Will add: ")
        print(*capa_filtered, sep=' ')
        card_ok += 1
        """
        capa_string=",".join(capa_filtered)
        sql = "UPDATE `ALL_CARDS` SET `Capa`='"+capa_string+"' WHERE `cle`="+str(cle)
        print("REQUEST= " + sql)
        db_cursor.execute(sql)
        mydb.commit()
        

    """
    if faction == "Pureté Céleste":
        cv2.imwrite("./detected/pc/edited_image" + str(i) + ".png", card)
    elif faction == "Nuit sans fin":
        cv2.imwrite("./detected/n/edited_image" + str(i) + ".png", card)
    elif faction == "Éondra":
        cv2.imwrite("./detected/e/edited_image" + str(i) + ".png", card)
    elif faction == "Métascience":
        cv2.imwrite("./detected/m/edited_image" + str(i) + ".png", card)
    elif faction == "Temple de la lumière":
        cv2.imwrite("./detected/tdll/edited_image" + str(i) + ".png", card)
    elif faction == "Poseidia":
        cv2.imwrite("./detected/p/edited_image" + str(i) + ".png", card)
    elif faction == "La voie":
        cv2.imwrite("./detected/v/edited_image" + str(i) + ".png", card)
    """


    #cv2.imwrite("./edited_image" + str(i) + ".png", card)
    i+=1
    all_card += 1
    
    #if i==20:
    #    break
    
    #print("---")

print("All card = " + str(all_card));
print("Probably found = " + str(card_ok));

