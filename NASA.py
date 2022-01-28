import requests
import urllib.request
import json
import os
import cv2
import shutil
import imageio as iio
import glob
import Tokens
from PIL import Image
from pygifsicle import optimize
from datetime import date

# Request example - https://api.nasa.gov/planetary/apod?api_key=KEY
class NASA:
    # Perseverance API URL and Key
    def __init__(self):
        self.__url = "https://api.nasa.gov/mars-photos/api/v1/rovers/perseverance/photos?"
        self.__key = Tokens.NASA_API_KEY

    # Get date of day before yesterday.. Day-2 seems to be the timeline for new images 
    def dayBeforeYesterday(self):
        todaysDate = date.today()
        twoDaysAgo = str(todaysDate.year) + "-" + str(todaysDate.month) + "-" + str(todaysDate.day - 2)
        self.date = twoDaysAgo
        self.dateDirectory = os.getcwd() + '/' + self.date
        self.__url = self.__url + "earth_date=" + twoDaysAgo + "&api_key=" + self.__key

    # Request all images from a given date
    def requestData(self):
        self.content = json.loads(requests.get(self.__url).content)
        if not (len(self.content) > 0): return False

    # Sort images by camera that took them
    def sortDataByCamera(self):
        cams = list()
        self.photos = Photos()
        for tree in self.content['photos']:
            if not tree['camera']['full_name'] in cams:
                cams.append(tree['camera']['full_name'])
                tempList = list()
                tempList.append(tree)
                self.photos.data.append(tempList)
                continue
            for x in range(0, len(self.photos.data)):
                if not self.photos.data[x][0]['camera']['full_name'] == tree['camera']['full_name']: continue
                self.photos.data[x].append(tree)
                break

    # Create directory for date and camera specific directories inside it
    # Go to image URLs can save images to their respective directories
    def fetchPhotos(self):
        try:
            os.mkdir(self.dateDirectory)
        except:
            print("Directory exists")
        for index in range(0, len(self.photos.data)):
            cameraDirectory = self.dateDirectory + '/' + str(self.photos.data[index][0]['camera']['name'])
            os.mkdir(cameraDirectory)
            imageCount = 1
            for data in self.photos.data[index]:
                fileName = str(imageCount) + ".jpg"
                urllib.request.urlretrieve(data['img_src'], fileName)
                shutil.move(fileName, cameraDirectory + '/' + fileName)
                imageCount += 1

    # Use imageio to process images into a GIF
    # Downsized images to 512x390 so they stay under twitters 5MB media cap for mobile devices
    def makeGif(self):
        self.filePaths = list()
        
        for _, folderNames, _ in os.walk(self.dateDirectory):
            break
        for folder in folderNames:
            images = list()
            for currentPath, _, fileNames in os.walk(self.dateDirectory + '/' + folder):
                break

            gifName = str(folder) + ".gif"
            self.filePaths.append(self.dateDirectory + '/' + folder + '/' + str(folder) + ".gif")
            fileNames = sortFunc(fileNames)

            if not (len(fileNames) > 1): 
                os.rename(currentPath + '/' + fileNames[0], currentPath + '/'  + folder + '.jpg')
                continue

            for file in fileNames:
                img = iio.imread(currentPath + '/' + file)
                img = Image.fromarray(img).resize((512, 390))
                images.append(img)

            # Save GIF with a 0.25s delay between each image
            iio.mimsave(currentPath + '/' + gifName, images, duration = 0.25)
            # Compress GIF
            optimize(currentPath + '/' + gifName)

    def makeVideo(self):
        self.filePaths = list()
        
        for _, folderNames, _ in os.walk(self.dateDirectory):
            break
        for folder in folderNames:
            
            for currentPath, _, fileNames in os.walk(self.dateDirectory + '/' + folder):
                break

            self.filePaths.append(self.dateDirectory + '/' + folder + '/' + str(folder) + ".avi")

            if not (len(fileNames) > 1): 
                os.rename(currentPath + '/' + fileNames[0], currentPath + '/'  + folder + '.jpg')
                continue
            
            img_array = []
            for filename in glob.glob(currentPath + '/' + '*.jpg'):
                img = cv2.imread(filename)
                img = cv2.resize(img, (512, 390),  interpolation = cv2.INTER_AREA)
                size = img.shape[:2]
                img_array.append(img)
            
            codec = cv2.VideoWriter_fourcc('X', 'V', 'I', 'D')
            out = cv2.VideoWriter(folder + '.avi',codec, 1/20, (size[1],size[0]))
            
            for i in range(len(img_array)):
                out.write(img_array[i])
            out.release()
            # for file in fileNames:
            #     img = iio.imread(currentPath + '/' + file)
            #     img = Image.fromarray(img).resize((512, 390))
            #     video.write(cv2.imread(img))

            # cv2.destroyAllWindows()
            # video.release()


class Photos:
    def __init__(self):
        self.data = list()

# Swaps the positions of items in a list
def swapPositions(list, pos1, pos2):
    list[pos1], list[pos2] = list[pos2], list[pos1]
    return list

# Sort images by ascending number
def sortFunc(fileNames):
    unsorted = True
    unsupportedFiles = True
    while (unsupportedFiles):
        for index in range(0, len(fileNames)):
            if not (fileNames[index][-3:] == "jpg"):
                fileNames.pop(index)
                unsupportedFiles = True
                break
            unsupportedFiles = False
    while (unsorted):
        for index in range(0, len(fileNames)):
            if (index + 1 == len(fileNames)):
                break
            if (int(fileNames[index][:-4]) > int(fileNames[index + 1][:-4])):
                swapPositions(fileNames, index, index + 1)
        checkUnsorted = False
        for index in range(0, len(fileNames)):
            if (index + 1 == len(fileNames)):
                break
            if (int(fileNames[index][:-4]) > int(fileNames[index + 1][:-4])):
                checkUnsorted = True
                break
        if (checkUnsorted): continue
        unsorted = False

    return fileNames

# nasa = NASA()
# nasa.dayBeforeYesterday()
# nasa.requestData()
# nasa.sortDataByCamera()
# nasa.fetchPhotos()
# nasa.makeGif()