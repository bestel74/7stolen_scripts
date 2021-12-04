#!/usr/bin/python3
import os
import requests
from bs4 import BeautifulSoup, SoupStrainer
import urllib.request


LOCAL_FOLDER_PATH       = "../pics/"
LOCAL_DECK_FOLDER_PATH  = "../deck/"



def get_codex_pics(folder_name, url):
    html = requests.get(url).content
    images =  BeautifulSoup(html, 'html.parser').find_all('img')
    image_links =[]
    
    # Create local folder if needed
    if os.path.isdir(LOCAL_FOLDER_PATH + folder_name) == False:
        os.mkdir(LOCAL_FOLDER_PATH + folder_name) 
        

    for image in images:
        
        # Test if the src image is in the good folder and not an "Ecusson"
        if image['src'].find(folder_name) != -1 and image['src'].find("Ecusson-") == -1:
            # valid image
            # print("VALID: " + image['src'])
        
            if image['src'].find("https://") == -1:
                # relative path, try to prepend absolute
                print("FIX: " + "https://7fallen.com" + image['src'])
                image_links.append("https://7fallen.com" + image['src'])
            else:
                #print(image['src'])
                image_links.append(image['src'])
                
    for link in image_links:
        filename = link.split("/")[-1].split("?")[0]
        filepath = LOCAL_FOLDER_PATH + folder_name + "/" + filename

        # Download only if we do not have this file
        if os.path.exists(filepath) == False:
            urllib.request.urlretrieve(urllib.parse.quote(link, safe=':/'), filepath)
            print(filepath + " saved")



def get_immortel_list(url):
    html = requests.get(url).content
    immos =  BeautifulSoup(html, 'html.parser').find_all('div', class_="elementor-col-25")
    
    print("Immos...")
    
    # Create local folder if needed
    if os.path.isdir(LOCAL_DECK_FOLDER_PATH) == False:
        os.mkdir(LOCAL_DECK_FOLDER_PATH) 
    
    for immo in immos:
        if immo.find("a") != None:
            if immo.find("a").has_attr("href") == True:
                
                name = immo.find("a").find("img")['src'].split("/")[-1].split(".")[0]
                divinite = immo.find("h2").find('span').contents[0].split("Div : ")[1]
                href_url = 'https://7fallen.com/fr' + immo.find("a")['href']
                
                print("Name: " + name)
                print("Divinité: " + divinite)
                print("href: " + href_url)
                
                path = divinite + " - " + name
                
                # Create local folder if needed
                if os.path.isdir(LOCAL_DECK_FOLDER_PATH + path) == False:
                    os.mkdir(LOCAL_DECK_FOLDER_PATH + path) 

                get_immortel_deck(path, href_url)


def append_number(filename, number):
    name, ext = os.path.splitext(filename)
    return "{name}_{uid}{ext}".format(name=name, uid=number, ext=ext)



def copy_immortel_page(folder_name, url, num):
    filename = url.split("/")[-1].split("?")[0]
    filepath = LOCAL_DECK_FOLDER_PATH + folder_name + "/" + filename

    for x in range(num):
        tmp_filepath = append_number(filepath, x)

        # Download only if we do not have this file
        if os.path.exists(tmp_filepath) == False:
            urllib.request.urlretrieve(urllib.parse.quote(url, safe=':/'), tmp_filepath)

    print(tmp_filepath + " saved")



def get_immortel_deck(name, url):
    html = requests.get(url).content
    pages = BeautifulSoup(html, 'html.parser').find_all('div', class_="elementor-col-33")
    pages += BeautifulSoup(html, 'html.parser').find_all('div', class_="elementor-col-25")
    
    cards_detected = 0;
  
    for page in pages:
        if page.find("img") != None:
            if page.find("img").has_attr("src") == True:
                page_img = page.find("img")['src']
                
                if page.find("h2") != None:
                    page_num = int(page.find("h2").find('span').contents[0].split("x")[1])
                else:
                    page_num = 1

            print("Img: " + page_img);
            print("num: " + str(page_num));
            
            copy_immortel_page(name, page_img, page_num);
            
            cards_detected += page_num

    print(str(cards_detected) + " cards detected")





get_codex_pics("LCDS", 'https://7fallen.com/fr/content/61-codex-eondra-lcds')
get_codex_pics("LCDS", 'https://7fallen.com/fr/content/62-codex-poseidia-lcds')
get_codex_pics("LCDS", 'https://7fallen.com/fr/content/63-codex-nuit-sans-fin-lcds')
get_codex_pics("LCDS", 'https://7fallen.com/fr/content/64-codex-metascience-lcds')
get_codex_pics("LCDS", 'https://7fallen.com/fr/content/65-codex-miracle-lcds')
get_codex_pics("TDLL", 'https://7fallen.com/fr/content/28-codex-temple-de-la-lumiere')
get_codex_pics("Purete_celeste", 'https://7fallen.com/fr/content/30-codex-purete-celeste')
get_codex_pics("LA VOIE", 'https://7fallen.com/fr/content/67-codex-la-voie')
get_codex_pics("ANAYA", 'https://7fallen.com/fr/content/70-codex-anaya')

get_immortel_list('https://7fallen.com/fr/content/41-deck-lists-des-heros')










