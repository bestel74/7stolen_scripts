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

LOCAL_FOLDER_PATH       = "../pics/"
LOCAL_DECK_FOLDER_PATH  = "../deck/"
LOCAL_REF_FOLDER_PATH   = "../ref/"

MAX_COST_ALLOWED = int(10)
NB_THRESHOLD_NUMBERS = 150



cards = []

cards = [cv2.imread(file) for file in glob.glob("../pics/*/*.png")]
cards += [cv2.imread(file) for file in glob.glob("../pics/*/*.jpg")]

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



def read_left(card):
    height = card.shape[0]
    width = card.shape[1]

    if math.floor(width/10) == math.floor(height/10):
        # Jeton
        h1 = height-45
        h2 = height-20
        w1 = 100
        w2 = 120
    elif height > width:
        # normal card
        h1 = height-50
        h2 = height-20
        w1 = 20
        w2 = 70
    else:
        return ""

    bot_crop = card[h1:h2,w1:w2]

    gray = get_grayscale(bot_crop)
    bw = cv2.threshold(gray, NB_THRESHOLD_NUMBERS, 255, cv2.THRESH_BINARY)[1]
    selected_image = cv2.bitwise_not(bw)

    # converts the image to result and saves it into result variable
    custom_config = r"-l fra --psm 6 -c tessedit_char_whitelist=' X0123456789©+-'"
    result = pytesseract.image_to_string(selected_image, config=custom_config)
    
    # No result? Test again with raw image
    if result.strip() == "":
        selected_image = bot_crop
        result = pytesseract.image_to_string(selected_image, config=custom_config)

    #cv2.imwrite("./image_" + str(i) + "_L.png", selected_image)
    
    return result.strip().split()


def read_right(card):
    height = card.shape[0]
    width = card.shape[1]
    
    if math.floor(width/10) == math.floor(height/10):
        # Jeton
        h1 = height-50
        h2 = height-20
        w1 = width-120
        w2 = width-100
    elif height > width:
        # normal card
        h1 = height-50
        h2 = height-20
        w1 = width-70
        w2 = width-23
    else:
        return ""


    bot_crop = card[h1:h2,w1:w2]

    gray = get_grayscale(bot_crop)
    bw = cv2.threshold(gray, NB_THRESHOLD_NUMBERS, 255, cv2.THRESH_BINARY)[1]
    selected_image = cv2.bitwise_not(bw)

    # converts the image to result and saves it into result variable
    custom_config = r"-l fra --psm 6 -c tessedit_char_whitelist=' X0123456789©+-'"
    result = pytesseract.image_to_string(selected_image, config=custom_config)
    
    # No result? Test again with raw image
    if result.strip() == "":
        selected_image = bot_crop
        result = pytesseract.image_to_string(selected_image, config=custom_config)

    #cv2.imwrite("./image_" + str(i) + "_R.png", selected_image)

    return result.strip().split()



def read_temple_ado(card):
    height = card.shape[0]
    width = card.shape[1]
    h1 = int((height/2)+50)
    h2 = int((height/2)+95)
    w1 = int((width/2)-15)
    w2 = int((width/2)+15)

    bot_crop = card[h1:h2,w1:w2]

    gray = get_grayscale(bot_crop)
    bw = cv2.threshold(gray, NB_THRESHOLD_NUMBERS, 255, cv2.THRESH_BINARY)[1]
    selected_image = cv2.bitwise_not(bw)

    # converts the image to result and saves it into result variable
    custom_config = r"-l fra --psm 6 -c tessedit_char_whitelist=' X0123456789©'"
    result = pytesseract.image_to_string(selected_image, config=custom_config)
    
    #cv2.imwrite("./image_" + str(i) + "_ado.png", selected_image)
    
    return result.strip().split()

    
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
        h2 = height-30
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
    selected_image = cv2.bitwise_not(gray)

    # converts the image to result and saves it into result variable
    custom_config = r'-l fra --psm 3'
    result = pytesseract.image_to_string(selected_image, config=custom_config)
    
    #cv2.imwrite("./image_" + str(i) + "_name.png", selected_image)
    
    return result.strip()


def read_type(card):
    height = card.shape[0]
    width = card.shape[1]

    if height > width:
        h1 = height-30
        h2 = height-15
        w1 = 120
        w2 = width-120
    else:
        h1 = height-40
        h2 = height-20
        w1 = int((width/2)+25)
        w2 = width-80

    bot_crop = card[h1:h2,w1:w2]

    gray = get_grayscale(bot_crop)
    selected_image = cv2.bitwise_not(gray)

    # converts the image to result and saves it into result variable
    custom_config = r'-l fra --psm 6'
    result = pytesseract.image_to_string(selected_image, config=custom_config)
    
    #cv2.imwrite("./image_" + str(i) + "_type.png", selected_image)

    return result.strip()

def read_faction(card):

    height = card.shape[0]
    width = card.shape[1]

    if height > width and math.floor(width/10) != math.floor(height/10):
        h1 = 30
        h2 = 70
        w1 = int((width/2)-25)
        w2 = int((width/2)+25)
    else:
        h1 = height-60
        h2 = height-20
        w1 = int((width/2)-25)
        w2 = int((width/2)+25)
    faction_crop = card[h1:h2,w1:w2]
    pixels = np.float32(faction_crop).reshape((-1, 3))

    n_colors = 1
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
    ret, label, center = cv2.kmeans(pixels, n_colors, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

    center = np.uint8(center)
    # Replace pixel values with their center value:
    result = center[label.flatten()]
    result = result.reshape(faction_crop.shape)
    
    hsv = cv2.cvtColor(result, cv2.COLOR_BGR2HSV)
    
    #cv2.imwrite("./image_" + str(i) + "_faction.png", faction_crop)
    #cv2.imwrite("./image_" + str(i) + "_faction_color.png", result)
    
    h,s,v = cv2.split(hsv)

    hue = h[0][0]
    sat = s[0][0]
    val = v[0][0]

    #print(str(hue) + "/" + str(sat) + "/" + str(val))

    if sat < 20 and val > 160:
        return "Pureté Céleste"
    elif sat < 30 and val <= 70:
        return "Nuit sans fin"
    elif hue <= 10:
        return "Éondra"
    elif hue <= 70 and sat <= 50:
        return "Métascience"
    elif hue <= 70 and sat > 50:
        return "Temple de la Lumière"
    elif hue <= 120:
        return "Poseidia"
    else:
        return "La voie"



i=0
for card in cards:    

    height = card.shape[0]
    width = card.shape[1]

    name = read_name(card)
    classe = read_type(card)
    left = read_left(card)
    right = read_right(card)
    faction = read_faction(card)
    
    read_faction(card)
    
    # Wrong space detection - 612 -> 6 12 - 51 -> 5 1
    if len(left) >= 1:
        if left[0].isdigit():
            if int(left[0]) >= 100:
                left.append( str( int(left[0]) %100 ) )
                left[0] = str( math.floor( int(left[0]) /100) )
            elif int(left[0]) >= MAX_COST_ALLOWED:
                left.append( str( int(left[0]) %10 ) )
                left[0] = str( math.floor( int(left[0]) /10) )
        elif left[0] == "©":
            left[0] = "0"
        elif left[0] == "XX":
            left[0] = "X"
            left.append("X")
        else:
            left[0] = 0
    if len(right) >= 1:
        if right[0].isdigit():
            if int(right[0]) >= 100:
                right.append( str( int(right[0]) %100 ) )
                right[0] = str( math.floor( int(right[0]) /100) )
            elif int(right[0]) >= MAX_COST_ALLOWED:
                right.append( str( int(right[0]) %10 ) )
                right[0] = str( math.floor( int(right[0]) /10) )
        elif right[0] == "©":
            right[0] = "0"
        elif right[0] == "XX":
            right[0] = "X"
            right.append("X")
        else:
            right[0] = 0
            
            
    # If a card got a class but no name (not possible) invert them
    if name=="" and classe!="":
        name = classe
        classe = ""

    specs=""
    ctype=""
    cost=""
    tempest=""
    fv=""
    atq=""
    bou=""
    ec=""
    tf=""
    ad=""
    adr=""
    
    
    if width > height:
        print("Divinité")
        ctype="Divinité"
        #cv2.imwrite("./detected/div/image" + str(i) + ".png", card)

    # If class is equipement, it's an equipement
    elif len(left) == 1 and len(right) == 1 and classe=="EQUIPEMENT":
        print("Equipement")
        ctype="Equipement"
        tempest = str(left[0])
        cost = str(right[0])
        specs += "TEMPEST " + tempest
        specs += "  COST " + cost
        #cv2.imwrite("./detected/equi/image" + str(i) + ".png", card)

    # no class type -> not angel but equipment
    elif len(left) == 2 and len(right) == 1 and classe=="":
        print("Epee")
        ctype="Equipement"
        faction="Neutre"
        atq = str(left[0])
        tempest = str(left[1])
        adr = str(right[0])
        specs += "ATQ " + atq
        specs += "  TEMPEST " + tempest
        specs += "  REV " + adr
        #cv2.imwrite("./detected/epee/image" + str(i) + ".png", card)
    
    elif width < height and len(left) == 0 and len(right) == 0:
        print("Temple ou Adorateur")
        ctype="Temple ou Adorateur"
        ec_tmp = read_temple_ado(card)
        if len(ec_tmp) >= 1:
            ec = str(ec_tmp[0])
        specs += "EC " + ec
        #cv2.imwrite("./detected/temp/image" + str(i) + ".png", card)

    elif len(left) >= 2 and len(right) >= 2:
        print("Archange")
        ctype="Archange"
        atq = str(left[0])
        fv = str(left[1])
        tf = str(right[0])
        ec = str(right[1])
        specs += "ATQ " + atq
        specs += "  FV " + fv
        specs += "  TF " + tf
        specs += "  EC " + ec
        #cv2.imwrite("./detected/arch/image" + str(i) + ".png", card)

    elif len(left) >= 2 and len(right) == 1:
        print("Ange")
        ctype="Ange"
        atq = str(left[0])
        fv = str(left[1])
        cost = str(right[0])
        specs += "ATQ " + atq
        specs += "  FV " + fv
        specs += "  COST " + cost
        #cv2.imwrite("./detected/ange/image" + str(i) + ".png", card)

    elif len(left) == 1 and len(right) == 1 and math.floor(width/10) == math.floor(height/10):  
        print("Familier")
        ctype="Familier"
        classe=""
        atq = str(left[0])
        fv = str(right[0])
        specs += "ATQ " + atq
        specs += "  FV " + fv
        #cv2.imwrite("./detected/jeton/image" + str(i) + ".png", card)
        
    elif len(left) == 1 and len(right) == 1 and classe!="":
        print("Golem")
        ctype="Golem"
        bou_tmp = read_temple_ado(card)
        if len(bou_tmp) >= 1:
            bou = str(bou_tmp[0])
        tempest = str(left[0])
        cost = str(right[0])
        specs += "BOU " + bou
        specs += "  TEMPEST " + tempest
        specs += "  COST " + cost
        #cv2.imwrite("./detected/golem/image" + str(i) + ".png", card)

    elif len(left) == 1 and len(right) == 1 and classe=="":
        print("Miracle")
        ctype="Miracle"
        faction="Neutre"
        ad = str(left[0])
        adr = str(right[0])
        specs += "ADO " + ad
        specs += "  REV " + adr
        #cv2.imwrite("./detected/mira/image" + str(i) + ".png", card)

    else:
        print("Error with left: " + str(len(left)) + " and right: " + str(len(right)))
        ctype="ERROR"
        #cv2.imwrite("./detected/err/image" + str(i) + ".png", card)

    
    result = "[" + faction + "] "
    result += name
    if classe != "":
        result += " ("
        result += classe
        result += ")"
    result += " : "
    result += specs
    
    print(result) 
    
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
    
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
    encimg = cv2.imencode('.jpg', card, encode_param)[1].tobytes()
    
    if ctype != "ERROR":
        sql_insert_blob_query = "INSERT INTO `"+MYSQL_TARGET_TABLE+"` (`cle`, `Carte`, `Faction`, `Type`, `Nom`, `Classe`, `Ec`, `Ft`, `Cout`, `Tmp`, `Atq`, `Fv`, `Bou`, `ado_cond`, `ado_rev`, `Capa`, `Texte`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, '', '');"
        insert_blob_tuple = (0, encimg, faction, ctype, name, classe, ec, tf, cost, tempest, atq, fv, bou, ad, adr)
    else:
        sql_insert_blob_query = "INSERT INTO `"+MYSQL_TARGET_TABLE+"` (`Carte`, `Extension`, `Faction`, `Nom`, `Classe`, `Ec`, `Ft`, `Cout`, `Tmp`, `Atq`, `Fv`, `Bou`, `ado_cond`, `ado_rev`, `Capa`, `Texte`, `Type`) VALUES (%s, %s, %s, %s, %s, '', '', '', '', '', '', '', '', '', '', '', '');"
        insert_blob_tuple = (encimg, 'Erreur', faction, name, classe)
 
    db_cursor.execute(sql_insert_blob_query, insert_blob_tuple)
    mydb.commit()
    print(db_cursor.rowcount, "Record Inserted")

    #cv2.imwrite("./edited_image" + str(i) + ".png", card)
    i+=1
    
    print("---")


