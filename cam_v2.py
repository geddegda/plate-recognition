import cv2
import os
from datetime import datetime

cap = cv2.VideoCapture("rtsp://user:password@ipadress:554/h264Preview_01_main")
w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
fps = cap.get(cv2.CAP_PROP_FPS) 

print(f"Resolution:{w}x{h}, FPS: {fps}")

saved_frame_count = 0
frame_count = 0
success,image= cap.read()

while success:
    if frame_count % 2 == 0:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename= f"frame_{ts}.jpg"
        cv2.imwrite(f"/home/guillaume/ram_videos/{filename}", image)
        print(f"Saved a new frame '{filename}' (# {saved_frame_count} ), Success={success}")
        saved_frame_count +=1


    frame_count += 1
    success,image = cap.read()

cap.release()
cv2.destroyAllWindows()
