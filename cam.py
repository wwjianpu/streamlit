from datetime import datetime 
import streamlit as st
from streamlit_webrtc import webrtc_streamer
import av
import cv2

class VideoProcessor:
    def __init__ (self) -> None:
        self.threshold1 = 100
        self.threshold2 = 200

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        img = cv2.cvtColor(cv2.Canny(img, self.threshold1, self.threshold2), cv2.COLOR_GRAY2BGR)
        img = cv2.putText(img, datetime.now().strftime("%H:%M:%S"), (3,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255,255), 2, cv2.LINE_AA)
        return av.VideoFrame.from_ndarray(img, format="bgr24")

def app_camera_test():
    """Simple video lookup"""
    st.write("hello")
    ctx = webrtc_streamer(key="example", video_processor_factory=VideoProcessor)
    if ctx.video_processor:
        ctx.video_processor.threshold1 = st.slider("Threshold1", min_value=0, max_value=1000, step=1, value=100)
        ctx.video_processor.threshold2 = st.slider("Threshold2", min_value=0, max_value=1000, step=1, value=200)
    st.write("testing")

def app_page2():
    """2222"""
    st.write("page 2")
    st.snow()

def app_page3():
    st.write("page 3")
    st.balloons()

def main():
    st.header("camera test")

    camera_test_page = (
        "Camera test page"
    )
    page2 = ("temp page 2")
    page3 = ("temp page 3")

    app_mode = st.sidebar.selectbox(
        "choose the app mode",
        [
            camera_test_page,
            page2,
            page3,
        ],
    )
    st.subheader(app_mode)

    if app_mode == camera_test_page:
        app_camera_test()
    elif app_mode == page2:
        app_page2()
    elif app_mode == page3:
        app_page3()


    st.sidebar.markdown(
        """
        hello
        """
    )

if __name__ == "__main__":
    main()