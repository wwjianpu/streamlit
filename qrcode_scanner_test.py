from datetime import datetime
from select import select
import time
import streamlit as st
import numpy as np
from streamlit_webrtc import webrtc_streamer
import av
import cv2

def main():


    class VideoProcessor:

        def __init__(self) -> None:
            self.d = cv2.QRCodeDetector()
            self.startcapture = False
            self.captured = False
            self.value = ""

        def recv(self, frame): 
            
            img = frame.to_ndarray(format="bgr24")
            val, points = self.d.detect(img)

            if val:
                qrcode_val, points, straight_qrcode = self.d.detectAndDecode(img)
                img = cv2.polylines(img, [points.astype(int)], True, (0,255,0), 2)

                if self.startcapture:
                    if (qrcode_val):
                        self.value = qrcode_val
                        self.startcapture = False
                        self.captured = True
                        print("capture OFF ", qrcode_val)

            return av.VideoFrame.from_ndarray(img, format="bgr24")



    frame_rate = 10
    ctx = webrtc_streamer(key="scanner", video_processor_factory=VideoProcessor, 
        media_stream_constraints={
            "video": {
                "frameRate": {"ideal": frame_rate}, 
                "width": 640 },            
            "audio": False, },
            async_processing=True)
    
    if 'start_time' not in st.session_state:
        st.session_state['start_time'] = datetime.now().strftime("%H:%M:%S")
    
    if 'cap' not in st.session_state:
        st.session_state['cap'] = False
    
    
    clicked = st.button("capture", key="btn_cap")
    if clicked:
        if ctx.video_processor:
            st.session_state.cap = True
            ctx.video_processor.captured = False

    status = st.empty()
    status.write(st.session_state.start_time)
    output = st.empty()

    if ctx.video_processor:
        ctx.video_processor.startcapture = st.session_state.cap
        st.session_state['start_time'] = datetime.now().strftime("%H:%M:%S")

        status.write(st.session_state['start_time'] + " capturing : " + str(st.session_state.cap))


    while st.session_state.cap:
        time.sleep(0.2)
        if ctx.video_processor:
            print(datetime.now().strftime("%H:%M:%S"), ctx.video_processor.value)
            if ctx.video_processor.captured:
                
                status.write(st.session_state['start_time'] + " - " + datetime.now().strftime("%H:%M:%S") + " capturing: False")
                output.write(ctx.video_processor.value)
                
                st.session_state.cap = False
        else:
            break
    
    st.write(st.session_state)

if __name__ == "__main__":
    main()
