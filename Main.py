from datetime import date
from datetime import datetime
from Twitter import Twitter
from NASA import NASA
import time
import os

# Dictionary for twitter date conversion
Month = {
    "Jan" : "1",
    "Feb" : "2",
    "Mar" : "3",
    "Apr" : "4",
    "May" : "5",
    "Jun" : "6",
    "Jul" : "7","xxxxxx"
    "Nov" : "11",
    "Dec" : "12"
    }

class Date():
    def __init__(self):
        self.year = None
        self.month = None
        self.day = None
        self.time = None

def convertDate(dateString):
    date = Date()
    year = dateString[-4:]
    time = ""
    # Match a month in the dictionary
    for key in Month:
        if key in dateString:
            # After month is grabbed, get day and year
            # Twitter API date format is ugly.. ex. JAN 01 00:00:00 0000:2022 -> converted to 2022-01-01
            month = Month[key]
            index = dateString.find(key)
            counter = 4
            day = ""
            while True:
                if dateString[index + counter] == " ": break
                day += dateString[index + counter]
                counter += 1
            counter += 1
            while True:
                if dateString[index + counter] == " ": break
                time += dateString[index + counter]
                counter += 1
            break

    date.year = year
    date.month = month
    date.day = day
    date.time = time

    return date

# Call NASA API functions and convert images to GIFs
def getPhotos():
    nasa = NASA()
    nasa.dayBeforeYesterday()
    dataRetrieved = nasa.requestData()
    if not (dataRetrieved):
        return False
    nasa.sortDataByCamera()
    nasa.fetchPhotos()
    nasa.makeGif()
    return nasa




if __name__ == '__main__':
    # Initialize vars
    lastPosted = None
    twit = Twitter()

    # Get last tweet
    lastTweet = twit.getTimeline()
    while True:
        # Convert date to better format
        lastTweetDate = convertDate(lastTweet[0]['created_at'])

        # Get todays date and time
        todaysDate = date.today()
        todaysTime = datetime.now()

        # Check to see if appropriate amount of time has passed before we process and post
        if (str(todaysDate.year) == lastTweetDate.year) or (str(todaysDate.day) == lastTweetDate.day) or (str(todaysDate.month) == lastTweetDate.month):
            currentTime = todaysTime.strftime("%H:%M:%S")
            currentTime = currentTime.split(':')
            lastTweetTime = lastTweetDate.time.split(':')

            # Convert UTC to Central Time
            if int(lastTweetTime[0]) - 6 < 0:
                # Wrap time since it is retrieved in military time
                lastTweetTime[0] = str(24 - 6 + int(lastTweetTime[0]))
            else:
                lastTweetTime[0] = str(int(lastTweetTime[0]) - 6)
            
            # If X amount of time has passed process more images
            # This is set to atleast 1 hour, but I ideally wanted it to be once a day or every other day
            # My twitter API key was suspended after doing on series of posts.... so RIP
            # If I still had access to my API key, I would have written this to check to see if my last tweet was posted > 24 hrs from current time
            if (int(currentTime[0]) - int(lastTweetTime[0]) >= 1) and (int(currentTime[1]) > int(lastTweetTime[1])) or int(currentTime[0]) - int(lastTweetTime[0]) >= 2:
                
                # DEBUG -> Skips calling NASA API if GIFs are already generated
                # for _, folderNames, _ in os.walk('.'):
                #     break
                # pictureDate = folderNames[1]
                # for _, cameraFolders, _ in os.walk('./' + pictureDate):
                #     break
                # for folder in cameraFolders:
                #     fileName = './' + folder + '/' + folder + '.gif'
                #     cameraName = folder
                #     title = "Photos from the " + cameraName + " on " + pictureDate + "." " @NASAPersevere" + " #Perseverance #Mars #NASA"
                #     twit.post(fileName, title)

                # Call NASA API, reprocess images to GIFs, grab image info and post to twitter
                nasa = getPhotos()

                # If photos are unavailable... Sleep for 12 hours and check again
                if not (nasa):
                    time.sleep(43200)
                    continue

                for filePath in nasa.filePaths:
                    stringSplit = filePath.split('/')
                    cameraName = stringSplit[len(stringSplit) - 2]
                    title = "Photos from the " + cameraName + " on " + nasa.date + "." " @NASAPersevere" + " #Perseverance #Mars #NASA"
                    twit.post(filePath, title)

                    # if successful sleep for 24 hours
                    time.sleep(86400)

                lastTweet = twit.getTimeline()

