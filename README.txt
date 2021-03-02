# Queen Cell Motion Detector

Detecting life inside of a queen cell utilizing background subtraction 
from the opencv-python library

# Usage

To use this program, simply run and you will be presented with a menu with
4 options.

Option 1: Turns on the webcam to begin recording for a set period of time,
	  a default of 5 seconds, and creates a notification on whether or 
	  not movement was detected.

Option 2: Change the duration of the recording to any whole integer value,
	  fractional numbers will not work.

Option 3: When the scanning of one frame is complete use this option to move
	  onto the next. This will simply increment the frame by one and the
	  current cell number to 0

Option 4: Exits program

# Disclaimer

This is far from a complete project, and simply illustrates the desired functionality
of a viable commercial product proividing an effective and efficient industry solution.

# Acknowledgments

This program is a modification of a tutorial by Adrian Rosebrock, who is a Computer Vision/Deep Learning 
developer and researcher. To find the unmodified code go to the following link: 

https://www.pyimagesearch.com/2015/05/25/basic-motion-detection-and-tracking-with-python-and-opencv/