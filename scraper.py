import os
import requests
import timeit
from PIL import Image
from bs4 import BeautifulSoup
import html5lib
from sort_lib import bubble_sort_desc
from sort_lib import quickSort
from support_functions import write_to_json
from support_functions import read_json_to_dict

# ---------------------------------------------------------------------- #
def get_img_info(url):
    '''
    Takes a url as a argument. example: https://xkcd.com/????/
    Finds comic image from comics folder and extracts image name and size
    Returns a dictionary with filename,filesize and the image url
    '''
    try:
        html = requests.get(url)
    except requests.HTTPError as e:
        print(f"\033[93m\n Error on {url} {e} \033[0m \n")
        return None
    try:
        bs = BeautifulSoup(html.content, 'html5lib')
        #img_tag = bs.find('img', {'src':re.compile('\/\/imgs.xkcd.com\/comics\/*')}) #<-- Only for people who knows their regEx
        #image_url = img_tag.attrs['src'] #<-- Only for people who knows their regEx
        image_url = bs.find('div', {'id': 'comic'}).find('img')['src'] #<-- Alternativ metode 
        image_head = requests.head(f"HTTPS:{image_url}")
        filesize = image_head.headers['Content-Length']
        filename = os.path.basename(image_url)
         #filename = image_url[image_url.rfind("/")+1:] #<-- Alternativ metode uten bruk av os       
    except AttributeError as e:
        print(f"\033[93m\n Error on {url} {e} \033[0m \n")
        return None
    except TypeError as e:
        print(f"\033[93m\n Error on {url} {e} \033[0m \n")
        return None
    except:
        print(f"Error occured on {url}")
        return None

    img_info = {
        'filename':filename,
        'filesize':filesize,
        'url':image_url
    }
    return img_info
# ---------------------------------------------------------------------- #
def save_data_to_json(): #Kan kanskje fjernes...
    '''Asking user if scraped data should be saved in a json file.
    Returns true if yes and false if no
    '''
    userinput = input("Would you like to save the data in a json.file? y/n  ").lower()
    if userinput == "y":
        return True
    elif userinput  == "n":
        return False
    else:
        print("Wrong input! Try again")
        return save_data_to_json()
# ---------------------------------------------------------------------- #
def number_of_pages_to_scrape():
    '''Asking user how many pages to scrape. Returns int number between 2 and 2380
    '''
    try:
        userinput = int(input("How many pages would you like to try to scrape?  "))
        if userinput in range(2,2381):
            return userinput
        else: 
            print("Input must be an integer between 2 and 2380")
            number_of_pages_to_scrape()
    except:
        print("Input must be an integer between 2 and 2380")
        number_of_pages_to_scrape()
# -----------------------------------------------------------------------------------------
def chosen_json_file():
    '''
    Asking user what json file to use.
    scraped.json or scraped_all.json
    '''
    user_choice = 0
    valid_range = range(1,3)
    while user_choice not in valid_range:
        try:
            user_choice = int(input('''\nWitch data set would you like to use? (choose 1 og 2):
                1 : The data just collected, \"scraped.json\"
                2 : Data stored in \"scraped_all.json\"
                '''))
            if user_choice not in valid_range:
                print("\033[93m\nHave you lost your glasses? Please choose 1 or 2\033[0m")
        except:
            print("\033[93m\nInput must be a interger. Please choose 1 or 2\033[0m")

    if user_choice == 1:
        user_choice = "scraped.json"
    else:
        user_choice = "scraped_all.json"

    return user_choice

# ---------------------------------------------------------------------- #

def chosen_image_by_user():
    '''
    Asking user what image file to download and open.
    '''
    user_choice = None
    valid_range = range(10)
    while user_choice not in valid_range:
        try:
            user_choice = int(input("Choose from 0 to 9: "))

            if user_choice not in valid_range:
                print("\033[93m\nHave you lost your glasses? Please choose a number between 0 and 9\033[0m")
        except:
            print("\033[93m\nInput must be a interger. Please choose a number between 0 and 9\033[0m")
    return user_choice

# ---------------------------------------------------------------------- #

def download_and_open_image(img_url, img_name):
    response = requests.get(img_url)
    with open(img_name, "wb") as img_file:
        img_file.write(response.content)
    Image.open(img_name, mode='r').show()

# ___________________________________________________________ #
# -------------------- END OF FUNCTIONS --------------------  #
# ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾ #

clear = lambda : os.system('cls' if os.name == 'nt' else 'clear')
clear()
images_dict = {}
counter = 0
pages_to_scrape = number_of_pages_to_scrape()

start = timeit.default_timer()
#Burde brukt counter fordi eksempelvis 404 finnes ikke. Det lager krøll for sortering. 
#Endret fra id til counter
for id in range(1, pages_to_scrape + 1):
    clear()
    print(f"You chose {pages_to_scrape} pages to scrape.")
    print(f"Trying to fetch comic from https://xkcd.com/{id}/")
    image_info = get_img_info(f"https://xkcd.com/{id}/")
    if image_info != None:
        images_dict[counter] = image_info
        counter += 1

end = timeit.default_timer()

print ("Scraped in:", end-start,"seconds") #1428 sec for all 2369 pictures

#if save_data_to_json():
#    pass #Alltid lagre som JSON forenkler valgene senere.

#writes images_dict to scraped.json in current folder
write_to_json(images_dict,"scraped.json") 

#Takes input from user and stores chosen json.file in in a dictionary
dict_from_json = read_json_to_dict(chosen_json_file()) 
dict_to_output = {}

#Converts ID and filesize from string to int in a new dictionary
for key,value in dict_from_json.items():
    dict_to_output[int(key)] = value
    dict_to_output[int(key)]['filesize'] = int(dict_from_json[key]['filesize'])

#sorts the dictionary by filesize in descending order
#dict_to_output = bubble_sort_desc(dict_to_output)
quickSort(dict_to_output, 0, len(dict_to_output)-1)

#Prints top10 of sorted dicrionary, with coulmn formatting
print("{:<4s}{:<10s}{:>6s}".format("#","Size","Filename"))
for key, value in dict_to_output.items():
    print("{:<4d}{:<10d}{:>6s}".format(key, value['filesize'], value['filename']))
    if key >= 9: break

input_from_user = chosen_image_by_user() #Gets int input from user, between 1 and 10

#Kunne langt inn https: i url når den scrapes... 
download_and_open_image(f"https:{dict_to_output[input_from_user]['url']}",dict_to_output[input_from_user]["filename"])
