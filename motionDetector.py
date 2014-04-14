import cv2
import urllib 
import numpy as np
import socket
import pygame
import time

class MotionDetector(object):
    def __init__(self):
        
        # Set up bad regions
        self.badX1 = 0
        self.badX2 = 1
        self.badY1 = 0
        self.badY2 = .5
        
        start = time.time()
        lastBad = start
        lastCat = start
        

        self.stream=urllib.urlopen('http://192.168.0.174:8080/videofeed')
        self.bytes=''  
        self.winName = "Movement Indicator"
        cv2.namedWindow(self.winName, cv2.CV_WINDOW_AUTOSIZE)

        # Read three images first:
        self.t_minus = cv2.cvtColor(self.getImage(), cv2.COLOR_RGB2GRAY)
        self.t = cv2.cvtColor(self.getImage(), cv2.COLOR_RGB2GRAY)
        self.t_plus = cv2.cvtColor(self.getImage(), cv2.COLOR_RGB2GRAY)
        
        self.height,self.width = self.t.shape

        while True:
          self.diff_t = self.diffImg(self.t_minus, self.t, self.t_plus)
          
          self.badArea = self.diff_t[self.height*self.badY1:self.height*self.badY2 ,self.width*self.badX1:self.width*self.badX2]
          
          
          cv2.imshow( self.winName, self.diff_t )
          print self.height*self.badY1 , self.height*self.badY2 , self.width*self.badX1 , self.width*self.badX2
          
          
          # Read next image
          self.t_minus = self.t
          self.t = self.t_plus
          self.t_plus = cv2.cvtColor(self.getImage(), cv2.COLOR_RGB2GRAY)
          
         
          totalMovement = cv2.countNonZero(cv2.inRange(self.diff_t,100,255))
          
          totalMovementBad = cv2.countNonZero(cv2.inRange(self.badArea,100,255))

          
          print totalMovement,totalMovementBad
          
          if totalMovement - totalMovementBad > 50:
            elapsedCat = (time.time() - lastCat)
            if elapsedCat > 5:
                u = urllib.urlopen("http://localhost:5000/catAppears", '')
                print 'cat!'
                lastCat = time.time()
          if totalMovementBad > 50:
            elapsedBad = (time.time() - lastBad)
            if elapsedBad > 5:
                pygame.mixer.init()
                pygame.mixer.music.load("ahh.wav")
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy() == True:
                    continue
                lastBad = time.time()
          
          key = cv2.waitKey(10)
          if key == 27:
            cv2.destroyWindow(self.winName)
            break

    def inverte(self,imagem):
        imagem = (255-imagem)
        return imagem
        #cv2.imwrite(name, imagem)
        
    def diffImg(self, t0, t1, t2):
        self.d1 = cv2.absdiff(t2, t1)
        self.d2 = cv2.absdiff(t1, t0)
        return cv2.bitwise_and(self.d1, self.d2)

    def getImage(self):
        #global bytes
        while True:
            self.bytes+=self.stream.read(1024)
            self.a = self.bytes.find('\xff\xd8')
            self.b = self.bytes.find('\xff\xd9')
            if self.a!=-1 and self.b!=-1:
                self.jpg = self.bytes[self.a:self.b+2]
                self.bytes= self.bytes[self.b+2:]
                i = cv2.imdecode(np.fromstring(self.jpg, dtype=np.uint8),cv2.CV_LOAD_IMAGE_COLOR)
                return i

if __name__ == '__main__':
	s = MotionDetector()