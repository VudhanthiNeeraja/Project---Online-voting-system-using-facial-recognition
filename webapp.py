import streamlit as st
import webbrowser
from PIL import Image

import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime,date
import time

import mysql.connector
db = mysql.connector.connect(
    host="localhost",
    user='root',
    passwd='1236',
    database='testdatabase'
)
mycursor = db.cursor( buffered=True)

path = 'VotingImages'
images = []
classNames = []
myList = os.listdir(path)
print(myList)
for cl in myList:
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])

print(classNames)

def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

def markVoted(name):
    query = """SELECT Status FROM VoteStatus WHERE Name=%s"""
    tuple1 = name
    mycursor.execute(query,(tuple1,))
    status = mycursor.fetchone()
    #print(status)
    if status[0] == 'notvoted':
        query = """UPDATE VoteStatus SET Status = 'voted' where Name=%s"""
        tuple1 = name
        mycursor.execute(query, (tuple1,))
        db.commit()
    return status[0]

def getVoteCount(name):
    query = """SELECT Count FROM VoteStatus WHERE Name=%s"""
    tuple1 = name
    mycursor.execute(query, (tuple1,))
    votes = mycursor.fetchone();
    #print(votes)
    if votes[0] == 0:
        query = """UPDATE VoteStatus SET Count = 1 where Name=%s"""
        tuple1 = name
        mycursor.execute(query, (tuple1,))
        db.commit()
    return votes[0]

encodeListKnown = findEncodings(images)
# print(len(encodeListKnown))
print('Encoding complete')


def detect_faces(image):
    name = 'not registered'

    list1 = []
    #image = cv2.resize(image, (0, 0), None, 0.25, 0.25)
    #image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = np.array(image.convert('RGB'))
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    imageFaceLoc = face_recognition.face_locations(image)
    encodesImage = face_recognition.face_encodings(image, imageFaceLoc)
    for encodeFace, faceLoc in zip(encodesImage, imageFaceLoc):
        matches = face_recognition.compare_faces(encodeListKnown,encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown,encodeFace)
        matchIndex = np.argmin(faceDis)
        if matches[matchIndex]:
            name = classNames[matchIndex]
    if name != 'not registered':
        status = markVoted(name)
        votes = getVoteCount(name)
        if status == 'notvoted' and votes == 0:
            return 0
        elif status=='voted' and votes == 1:
            return 1
    else:
        return 2


def main():
    """Face Recognition App"""


    html_temp = """
    <body style="background-color:red;">
    <div>
    <h2 style="color:white;text-align:center; background-color:teal ;padding:10px">IDENTITY VERIFICATION</h2>
    <h3 style="color:white;text-align:center;">UPLOAD IMAGE </h3>
    </div>
    </body>
    """
    st.markdown(html_temp, unsafe_allow_html=True)
    list = []
    image_file = st.file_uploader("", type=['jpg', 'png', 'jpeg'])
    if image_file is not None:
        image = Image.open(image_file)
        st.text("Uploaded Image")
        st.image(image)
    # if st.button("Verify Identity"):
    #     num = detect_faces(image)
    #     if (num == 0):
    #         #st.button("VOTE")
    #         if st.button("VOTE"):
    #             url = 'num0.html'
    #             webbrowser.open_new_tab(url)
    #     elif(num==1):
    #         #st.button("ALREADY VOTED")
    #         if st.button("ALREADY VOTED"):
    #             url = 'num1.html'
    #             webbrowser.open_new_tab(url)
    #     elif(num==2):
    #         #st.button("NOT REGISTERED")
    #         if st.button("NOT REGISTERED"):
    #             url = 'num2.html'
    #             webbrowser.open_new_tab(url)

    if st.button("Verify Identity"):
        num = detect_faces(image)
        if(num==0):
            url = 'num0.html'
            webbrowser.open_new_tab(url)
        elif(num==1):
            url = 'num1.html'
            webbrowser.open_new_tab(url)
        elif(num==2):
            url = 'num2.html'
            webbrowser.open(url,new=0)

    # url = 'D:\Python Projects\VotingSystemProject\GFG.html'
    # if st.button('Open browser'):
    #     webbrowser.open_new_tab(url)

if __name__ == '__main__':
    main()
