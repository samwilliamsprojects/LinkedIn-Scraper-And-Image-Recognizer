import cv2

# loading the pretrained deep neural network model and the weights
gender_model = cv2.dnn.readNetFromCaffe("gender.prototxt", "gender.caffemodel")

# setting up face detector
detector_path = 'pretrainedModel/haarcascade_frontalface_default.xml'
detector = cv2.CascadeClassifier(detector_path)


# function to detect a face in an image
def detect_faces(image):
    # face detector works with certain color schemes, using grey here
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    face = detector.detectMultiScale(gray_image, 1.3, 5)
    return face


# function to predict gender using the gender model and face detector
def predict_gender(img):
    face = detect_faces(img)
    for x, y, w, h in face:
        # sets center of detected face
        detected_face = img[int(y):int(y+h), int(x):int(x+w)]

        # resizes the face for the model
        detected_face = cv2.resize(detected_face, (224, 224))
        detected_face_blob = cv2.dnn.blobFromImage(detected_face)

        # prepares model
        gender_model.setInput(detected_face_blob)

        # runs model
        gender_result = gender_model.forward()[0]

        # if first digit is higher, gender is female
        if float(gender_result[0]) > 0.5:
            return 'female'
        else:
            return 'male'
