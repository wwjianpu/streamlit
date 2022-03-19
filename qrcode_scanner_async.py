from datetime import datetime
import time
import streamlit as st
import numpy as np
from streamlit_webrtc import RTCConfiguration, VideoProcessorBase, webrtc_streamer, WebRtcMode
import av
import cv2
from typing import List, NamedTuple

RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

def main():
    class VideoProcessor(VideoProcessorBase):

        def __init__(self) -> None:
            self.d = cv2.QRCodeDetector()
            self.startcapture = False
            self.captured = False
            self.value = ""

        async def recv_queued(self, frames: List[av.AudioFrame]) -> List[av.VideoFrame]: 

            rtn_frames = []

            for frame in frames:
                img = frame.to_ndarray(format="bgr24")
                val, points = self.d.detect(img)

                if val:
                    img = cv2.polylines(img, [points.astype(int)], True, (0,255,0), 2)

                    if self.startcapture:
                        qrcode_val, points, straight_qrcode = self.d.detectAndDecode(img)
                        if (qrcode_val):
                            self.value = qrcode_val
                            self.startcapture = False
                            self.captured = True
                            #print("capture OFF ", qrcode_val)

                # get single frame for return only
                rtn_frames.append(av.VideoFrame.from_ndarray(img, format="bgr24"))
                break

            return rtn_frames



    frame_rate = 10
    ctx = webrtc_streamer(
        key="scanner", 
        mode=WebRtcMode.SENDRECV,
        video_processor_factory=VideoProcessor, 
        media_stream_constraints={
            "video": {
                "frameRate": {"ideal": frame_rate, "max": 15}, 
                "width": {"min": 800, "ideal": 1280, "max": 1920 }, },            
            "audio": False, },
        rtc_configuration=RTC_CONFIGURATION, 
        async_processing=True,
    )
    
    if 'start_time' not in st.session_state:
        st.session_state['start_time'] = datetime.now().strftime("%H:%M:%S")
    
    if 'cap' not in st.session_state:
        st.session_state['cap'] = False
    
    if 'qrcode_value' not in st.session_state:
        st.session_state['qrcode_value'] = ""
    
    
    # sidebar
    time_limit = st.sidebar.number_input("time limit (in second) for capturing ", min_value=1, max_value=300,value=20)
    time_limit = time_limit * 10

    with st.container():

        col1, col2 = st.columns(2)

        with col1:
            cap_clicked = st.button("capture", key="btn_cap")
            if cap_clicked:
                if ctx.video_processor:
                    st.session_state.cap = True
                    ctx.video_processor.captured = False

        with col2:

            # not work in "True" while loop without draw screen
            stop_clicked = st.button("stop capture", key="btn_stop")
            if stop_clicked:
                if ctx.video_processor:
                    st.session_state.cap = False
                    ctx.video_processor.captured = False

    status = st.empty()
    status.write(st.session_state.start_time)
    output = st.empty()

    if ctx.video_processor:
        ctx.video_processor.startcapture = st.session_state.cap
        st.session_state['start_time'] = datetime.now().strftime("%H:%M:%S")

        status.write(st.session_state['start_time'] + " capturing " + str(st.session_state.cap))

    ##obj = st.sidebar.checkbox('Capture')
    
    c = 0
    while st.session_state.cap:
        time.sleep(0.1)
        c = c + 1
        if ctx.video_processor and c < time_limit:
            # print(datetime.now().strftime("%H:%M:%S"), ctx.video_processor.value, c)
            status.write(st.session_state['start_time'] + " - capturing - " + str(time_limit - c))
            if ctx.video_processor.captured:
                
                status.write(st.session_state['start_time'] + " - captured - " + str(time_limit - c))
                
                st.session_state.qrcode_value = ctx.video_processor.value
                output.write(st.session_state.qrcode_value)
                ctx.video_processor.value = ""
                
                st.session_state.cap = False
        elif c == time_limit:
            status.write(st.session_state['start_time'] + " - " + datetime.now().strftime("%H:%M:%S") + " capturing: timeout")
            st.session_state.cap = False
        else:
            break
    with st.expander("session state"):
        st.write(st.session_state)

if __name__ == "__main__": 
    main()
