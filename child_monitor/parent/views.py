from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.views.generic import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from . forms import ParentForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User 
import cv2
import threading
import os
import serial
import time
import time, sounddevice as sd
from scipy.io.wavfile import write
import argparse
import pickle
import sys
import warnings
from . Files.Test.lib import Reader
from . Files.Test.lib.baby_cry_predictor import BabyCryPredictor
from . Files.Test.lib.feature_engineer import FeatureEngineer
from . Files.Test.lib.majority_voter import MajorityVoter
from  django.conf import settings
from django.core.mail import send_mail

class ParentView(CreateView):
    model = User
    form_class = ParentForm
    template_name = 'parent/signup.html'

    def form_valid(self, form):
        form.save()
        messages.success(self.request, f'Your account has been created! You are now able to login')
        return redirect('login')


def choice(request):
    return render(request, 'parent/choice.html')


def video_capture(request):
    filename = 'video.mp4'
    frames_per_second = 24.0
    res = '720p'

    # Set resolution for the video capture
    # Function adapted from https://kirr.co/0l6qmh
    def change_res(cap, width, height):
        cap.set(3, width)
        cap.set(4, height)

    # Standard Video Dimensions Sizes
    STD_DIMENSIONS =  {
        "480p": (640, 480),
        "720p": (1280, 720),
        "1080p": (1920, 1080),
        "4k": (3840, 2160),
    }


    # grab resolution dimensions and set video capture to it.
    def get_dims(cap, res='1080p'):
        width, height = STD_DIMENSIONS["480p"]
        if res in STD_DIMENSIONS:
            width,height = STD_DIMENSIONS[res]
        ## change the current caputre device
        ## to the resulting resolution
        change_res(cap, width, height)
        return width, height

    # Video Encoding, might require additional installs
    # Types of Codes: http://www.fourcc.org/codecs.php
    VIDEO_TYPE = {
        'avi': cv2.VideoWriter_fourcc(*'XVID'),
        'mp4': cv2.VideoWriter_fourcc(*'H264'),
        'mp4': cv2.VideoWriter_fourcc(*'XVID'),
    }

    def get_video_type(filename):
        filename, ext = os.path.splitext(filename)
        #print(ext)
        if ext in VIDEO_TYPE:
            return  VIDEO_TYPE[ext]
        return VIDEO_TYPE['mp4']



    cap = cv2.VideoCapture(0)
    out = cv2.VideoWriter(filename, get_video_type(filename), 25, get_dims(cap, res))
    start = time.time()
    end = time.time()
    while end-start < 25:
        ret, frame = cap.read()
        out.write(frame)
        cv2.imshow('image',frame)
        end = time.time()
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


    cap.release()
    out.release()
    cv2.destroyAllWindows()    

def audiorecording(request):
    fs=44100
    seconds=10

    myrecording = sd.rec(int(seconds*fs), samplerate=fs, channels=2)
    sd.wait()
    write('output.wav', fs, myrecording)
    return redirect('ai')

def ai(request):
    # Read signal
    
    file_name = 'op.wav'       # only one file in th
    file_reader = Reader(os.path.join(settings.BASE_DIR, file_name))
    play_list = file_reader.read_audio_file()

    # iterate on play_list for feature engineering and prediction

    # Feature extraction
    engineer = FeatureEngineer()

    play_list_processed = list()

    for signal in play_list:
        tmp = engineer.feature_engineer(signal)
        play_list_processed.append(tmp)

    # https://stackoverflow.com/questions/41146759/check-sklearn-version-before-loading-model-using-joblib
    with warnings.catch_warnings():
      warnings.simplefilter("ignore", category=UserWarning)

      with open((os.path.join(settings.BASE_DIR, 'model.pkl')), 'rb') as fp:
          model = pickle.load(fp)

    predictor = BabyCryPredictor(model)

    predictions = list()

    for signal in play_list_processed:
        tmp = predictor.classify(signal)
        predictions.append(tmp)

    majority_voter = MajorityVoter(predictions)
    majority_vote = majority_voter.vote()

    # Save prediction result
    with open(os.path.join(settings.BASE_DIR, 'prediction.txt'), 'wt') as text_file:
        text_file.write("{0}".format(majority_vote))

    return redirect('mail')


def sendmail(request):
    f = open(os.path.join(settings.BASE_DIR, 'prediction.txt'),'rt')
    content = f.read()
    v = int(content)
    if v==1:
        u=request.user
        email_list=[]
        email_list.append(u.email)
        send_mail("With Child", "Hey, "+"You child is crying" , request.user.email, email_list)
        messages.success(request, f'Mail Sent!')
        try:
            ser = serial.Serial('COM6',9600)
            lfile=open(os.path.join(settings.BASE_DIR,'parent/sample.csv'), 'r+')
            while 1:
                line=lfile.readline()
                if not line:
                    break
                ser.write(line.encode())
                time.sleep(0.5)
        except:
            print()
        print()
    elif v==2:
        try:
            ser = serial.Serial('COM6',9600)
            lfile=open(os.path.join(settings.BASE_DIR,'parent/sample.csv'), 'r+')
            while 1:
                line=lfile.readline()
                if not line:
                    break
                ser.write(line.encode())
                time.sleep(3)
        except:
            print()
    
    elif v==3:
        try:
            ser = serial.Serial('COM6',9600)
            lfile=open(os.path.join(settings.BASE_DIR,'parent/sample.csv'), 'r+')
            while 1:
                line=lfile.readline()
                if not line:
                    break
                ser.write(line.encode())
                time.sleep(1)
        except:
            print()

    elif v==4:
        try:
            ser = serial.Serial('COM6',9600)
            lfile=open(os.path.join(settings.BASE_DIR,'parent/sample.csv'), 'r+')
            while 1:
                line=lfile.readline()
                if not line:
                    break
                ser.write(line.encode())
                time.sleep(1.25)
        except:
            print()


    else:
        print()

    return redirect('signup')
