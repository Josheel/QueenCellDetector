from imutils.video import VideoStream
import datetime
import imutils
import time
import cv2
import pyrebase

# Initialize Database
firebaseConfig = {
    "apiKey": "AIzaSyDPKjjucVXNG7mkDvQnGBXYxINTu3a54Oc",
    "authDomain": "queencelldatalog.firebaseapp.com",
    "databaseURL": "https://queencelldatalog-default-rtdb.firebaseio.com",
    "projectId": "queencelldatalog",
    "storageBucket": "queencelldatalog.appspot.com",
    "messagingSenderId": "725610986117",
    "appId": "1:725610986117:web:83d121dcc799bd058e87ec",
    "measurementId": "G-3LWV7F4V0Z"
}
firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()


# initialize camera and detection area
vs = VideoStream(src=0).start()
time.sleep(2.0)
min_area = 500

# initialize a date string and default length of capture
captureFullDate = datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p")
captureDate = datetime.datetime.now().strftime("%A %d %B %Y")
captureTime = datetime.datetime.now().strftime("%#I:%M:%S%p")
fileDate = datetime.datetime.now().strftime("%Y%b%d").upper()
seconds = 5

# open the data file and init variable and initialize other data variables
file = open(fileDate + '.txt', 'a+')
cellCount = 0
isAlive = False

# Get the value of current frame otherwise set it to 0
frameCount = db.child("frameCount").get().val()
if frameCount is None:
    frameCount = 0
    db.set({"frameCount": frameCount})

# Options Menu
menu = {'1': "Begin Capture (Press 'q' to end early)",
        '2': "Set Time (Default 5 Seconds)",
        '3': "Next Frame",
        '4': "Exit"}

while True:
    options = menu.keys()
    for entry in options:
        print(entry, menu[entry])

    selection = input("Please Select:")
    if selection == '1':
        # initialize the first frame in the video stream
        firstFrame = None
        start_time = time.time()

        while True:
            # grab the current frame and initialize the occupied/unoccupied
            # text
            frame = vs.read()
            frame = frame
            text = "No Movement"
            # if the frame could not be grabbed, then we have reached the end
            # of the video
            if frame is None:
                break
            # resize the frame, convert it to grayscale, and blur it
            frame = imutils.resize(frame, width=500)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)
            # if the first frame is None, initialize it
            if firstFrame is None:
                firstFrame = gray
                continue
            # compute the absolute difference between the current frame and
            # first frame
            frameDelta = cv2.absdiff(firstFrame, gray)
            thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
            # dilate the thresholded image to fill in holes, then find contours
            # on thresholded image
            thresh = cv2.dilate(thresh, None, iterations=2)
            cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE)
            cnts = imutils.grab_contours(cnts)
            # loop over the contours
            for c in cnts:
                # if the contour is too small, ignore it
                if cv2.contourArea(c) < min_area:
                    continue
                # compute the bounding box for the contour, draw it on the frame,
                # and update the text
                (x, y, w, h) = cv2.boundingRect(c)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                text = "Movement Detected"
                isAlive = True

            # draw the text and timestamp on the frame
            cv2.putText(frame, "Room Status: {}".format(text), (10, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            cv2.putText(frame, captureFullDate,
                        (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
            # show the frame and record if the user presses a key
            cv2.imshow("Cell Video Feed", frame)

            key = cv2.waitKey(1) & 0xFF
            # if the `q` key is pressed, break from the lop
            if key == ord("q"):
                break

            if key == ord("c"):
                write_to_file = " cell%d alive\n"
                file.write(captureTime + " " + write_to_file % cellCount)
                cellCount += 1

            current_time = time.time()
            elapsed_time = current_time - start_time

            if elapsed_time > seconds:
                break

        # Check cell health
        if isAlive:
            # Upload to database
            cell = "Cell%d" % cellCount
            frame = "Frame%d" % frameCount
            data = {captureTime: "Alive"}
            db.child(fileDate).child(frame).child(cell).set(data)

            # Write to file
            write_to_file = " cell %d alive\n"
            file.write(captureTime + " " + write_to_file % cellCount)
            cellCount += 1
            print('Cell is alive\n')

        else:
            # Upload to data base
            cell = "Cell%d" % cellCount
            frame = "Frame%d" % frameCount
            data = {captureTime: "Dead"}
            db.child(fileDate).child(frame).child(cell).set(data)

            # Write to file
            write_to_file = " cell %d dead\n"
            file.write(captureTime + " " + write_to_file % cellCount)

            cellCount += 1
            print('Cell is dead\n')

        # cleanup the camera and close any open windows
        cv2.destroyAllWindows()
        isAlive = False

    elif selection == '2':
        seconds = int(input("Enter capture length in seconds: "))
        print()

    elif selection == '3':
        frameCount += 1
        db.child("frameCount").set(frameCount)
        print("Now scanning frame %d\n" % frameCount)
        file.write("\nFrame %d\n" % frameCount)
        cellCount = 0

    elif selection == '4':
        file.write("\n")
        vs.stop()
        file.close()
        break

    else:
        print("Invalid Option\n")
