import face_recognition
import cv2
import numpy as np
import datetime
import pickle
import openpyxl
import threading
import time
import random
import sendMail
from plyer import notification as msg

addedPerson = []


def actionForUnknown(image, timing):

    
    msg.notify(title="Warning" ,message= f"Unknown face detected {timing}" ,timeout= 5)
    
    global addedPerson
    time.sleep(3)
    if "Unknown" in addedPerson:
        sendMail.mailAlert(image, timing)
        addedPerson.remove("Unknown")


def recognizer():
    f=open("ref_name.pkl","rb")
    ref_dictt=pickle.load(f)
    f.close()

    f=open("ref_embed.pkl","rb")
    embed_dictt=pickle.load(f)
    f.close()
    known_face_encodings = []
    known_face_names = []


    for ref_id , embed_list in embed_dictt.items():
        for my_embed in embed_list:
            known_face_encodings +=[my_embed]
            known_face_names += [ref_id]

    video_capture = cv2.VideoCapture(0)

    face_locations = []
    face_encodings = []
    face_names = []
    person_entered= []
    process_this_frame = True
    # addedPerson = []
    global addedPerson

    while True:
        ret, frame = video_capture.read()

        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        #rgb_small_frame = small_frame[:, :, ::-1]
        rgb_small_frame = np.ascontiguousarray(small_frame[:, :, ::-1])

        if process_this_frame:

            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            face_names = []
            for face_encoding in face_encodings:

                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"

                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]
                face_names.append(name)

        process_this_frame = not process_this_frame


        for (top_s, right, bottom, left), name in zip(face_locations, face_names):
            top_s *= 4
            right *= 4
            bottom *= 4
            left *= 4

            cv2.rectangle(frame, (left, top_s), (right, bottom), (0, 200, 0), 2)

            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 200, 0), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX

            
            if name not in addedPerson:
                data = []
                
                atTime = datetime.datetime.now()
                atTime = str(atTime) 
                t = atTime
                day = t.split(" ")[0]
                tim = t.split(" ")[1]
                tims = tim.split(".")[0]
                atTime = f"on {day} at {tims}"

                if name == "Unknown":
                    imgIDSuffix = random.randint(1000, 9999)
                    imgName = f"./UnknownPersons/captured_image_{imgIDSuffix}.jpg"
                    cv2.imwrite(imgName, frame)
                    # print("Unknown Person Detected")
                    threading.Thread(target=actionForUnknown, args=(imgName,atTime)).start()
                    # actionForUnknown(imgName, atTime)
                    data.append("Not registered")
                    data.append(name)
                    data.append(atTime)

                else:
                    print(f"Person Entered : {ref_dictt[name]}, Date:{atTime.replace('on', '').replace('at','Time:')}" )
                    data.append(name)
                    data.append(ref_dictt[name])
                    data.append(atTime)

                person_entered.append(data)
                addedPerson.append(name)

            if name == "Unknown":
                cv2.putText(frame, "ALERT" , (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
            else:
                cv2.putText(frame, ref_dictt[name], (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.imshow('Video', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
        
#############Adding detetcted face to excel ####################

    workbook = openpyxl.load_workbook('DetectedData.xlsx')
    # Select the worksheet to append data to
    worksheet = workbook.active
    # Define the new data to be added
    new_data = person_entered
    # Append the new data to the worksheet
    for row in new_data:
        worksheet.append(row)

    # Save the updated workbook
    workbook.save('DetectedData.xlsx')


    video_capture.release()
    cv2.destroyAllWindows()
    
    
if __name__ == "__main__":
    recognizer()
