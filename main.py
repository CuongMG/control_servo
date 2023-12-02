import cv2
import mediapipe as mp
import math
import requests as r

url = 'https://control-servo-c8729-default-rtdb.firebaseio.com/.json'

json = {'angle': 0}

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

# For static images:
IMAGE_FILES = []
with mp_hands.Hands(
    static_image_mode=True,
    max_num_hands=2,
    min_detection_confidence=0.5) as hands:
  for idx, file in enumerate(IMAGE_FILES):
    # Read an image, flip it around y-axis for correct handedness output (see
    # above).
    image = cv2.flip(cv2.imread(file), 1)
    # Convert the BGR image to RGB before processing.
    results = hands.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    # Print handedness and draw hand landmarks on the image.
    print('Handedness:', results.multi_handedness)
    if not results.multi_hand_landmarks:
      continue
    image_height, image_width, _ = image.shape
    annotated_image = image.copy()
    for hand_landmarks in results.multi_hand_landmarks:
      print('hand_landmarks:', hand_landmarks)
      print(
          f'Index finger tip coordinates: (',
          f'{hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * image_width}, '
          f'{hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * image_height})'
      )
      mp_drawing.draw_landmarks(
          annotated_image,
          hand_landmarks,
          mp_hands.HAND_CONNECTIONS,
          mp_drawing_styles.get_default_hand_landmarks_style(),
          mp_drawing_styles.get_default_hand_connections_style())
    cv2.imwrite(
        '/tmp/annotated_image' + str(idx) + '.png', cv2.flip(annotated_image, 1))
    # Draw hand world landmarks.
    if not results.multi_hand_world_landmarks:
      continue
    for hand_world_landmarks in results.multi_hand_world_landmarks:
      mp_drawing.plot_landmarks(
        hand_world_landmarks, mp_hands.HAND_CONNECTIONS, azimuth=5)

count = 0

# For webcam input:
cap = cv2.VideoCapture(0)
with mp_hands.Hands(
    model_complexity=0,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands:
  while cap.isOpened():
    success, image = cap.read()
    if not success:
      print("Ignoring empty camera frame.")
      # If loading a video, use 'break' instead of 'continue'.
      continue

    # To improve performance, optionally mark the image as not writeable to
    # pass by reference.
    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image)

    # Draw the hand annotations on the image.
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    height, width, _ = image.shape

    if results.multi_hand_landmarks:
      count += 1
      hand_centers_8 = []
      hand_centers_4 = []

      for hand_landmarks in results.multi_hand_landmarks:
        hand_centers_8.append([int(hand_landmarks.landmark[8].x * width), int(hand_landmarks.landmark[8].y * height)])
        hand_centers_4.append([int(hand_landmarks.landmark[4].x * width), int(hand_landmarks.landmark[4].y * height)])

        mp_drawing.draw_landmarks(
            image,
            hand_landmarks,
            mp_hands.HAND_CONNECTIONS,
            mp_drawing_styles.get_default_hand_landmarks_style(),
            mp_drawing_styles.get_default_hand_connections_style())
    # Flip the image horizontally for a selfie-view display.
      if(len(hand_centers_8) == 1 and len(hand_centers_4) == 1):
        cv2.line(image, (hand_centers_8[0][0], hand_centers_8[0][1]),
                 (hand_centers_4[0][0], hand_centers_4[0][1]), (0, 255, 0), 5)

        angle = math.degrees(math.atan2(hand_centers_8[0][1] - hand_centers_4[0][1],
                                        hand_centers_8[0][0] - hand_centers_4[0][0]))
        if count % 60 == 0:

	  if angle < 0:
  	    angle += 360

	    print(angle) # In ra 270 độ

	  if angle > 180:
  	    angle -= 360
  
	    print(angle) # In ra 90 độ (nằm trong khoảng 0-180)
          json['angle'] = int(angle)
          response = r.put(url=url, json=json)

    cv2.imshow('MediaPipe Hands', cv2.flip(image, 1))
    if cv2.waitKey(5) & 0xFF == 27:
      break
cap.release()




