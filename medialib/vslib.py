import time
from threading import Thread, Lock
from typing import Union

import cv2

import medialib
from loglib.loglib import loglib


class vslib:
    """
    The library for camera video stream.

    reference: https://gist.github.com/allskyee/7749b9318e914ca45eb0a1000a81bf56
    """

    slogger = loglib('__name__')

    def __init__(self, src: Union[int, str] = 0, width: int = 0, height: int = 0):
        self.update_thread = None
        import datetime
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S.%f')
        self.logger = loglib(f'{__name__}_time{timestamp}')

        self.src = src
        self.stream = cv2.VideoCapture(src)
        if width and height:
            self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.logger.info(f'(w, h, fps, fcnt): {self.getinfo()}')
        if type(src) == int:
            (self.grabbed, self.frame) = self.stream.read()
        self.started = False
        self.read_lock = Lock()

    # region [camera]
    def start(self):
        if self.started:
            self.logger.warning('already started!!!')
            return None
        self.started = True
        self.update_thread = Thread(target=self.update, args=())
        self.update_thread.start()
        return self

    def update(self):
        while self.started:
            (grabbed, frame) = self.stream.read()
            self.read_lock.acquire()
            self.grabbed, self.frame = grabbed, frame
            self.read_lock.release()

    def read(self):
        self.read_lock.acquire()
        frame = None
        if self.frame is not None:
            frame = self.frame.copy()
        else:
            self.logger.error('frame is None!!!')
        self.read_lock.release()
        return frame

    def stop(self):
        self.started = False
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join()

    # endregion [camera]

    # region [video]
    def _read(self):
        """
        directly read for video case
        """
        (self.grabbed, self.frame) = self.stream.read()
        return self.frame

    # endregion [video]

    # region [function]
    def set(self, propid: int, value: int):
        self.stream.set(propId=propid, value=value)

    def is_opened(self):
        return self.stream.isOpened()

    def release(self):
        # stop before release
        self.stop()
        self.stream.release()

    def getinfo(self):
        w = self.stream.get(cv2.CAP_PROP_FRAME_WIDTH)
        h = self.stream.get(cv2.CAP_PROP_FRAME_HEIGHT)
        fps = self.stream.get(cv2.CAP_PROP_FPS)
        fcnt = self.stream.get(cv2.CAP_PROP_FRAME_COUNT)
        return w, h, fps, fcnt

    @staticmethod
    def get_cam_list(scan_count: int = 10):
        """
        get valid camera list

        Parameters
        ----------
        scan_count : int
            how many cameras to scan

        Returns
        -------
        list
            valid camera list
        """

        cams = []
        for index in range(scan_count):
            cap = cv2.VideoCapture(index)
            if cap and cap.isOpened():
                if not cap.read()[0]:
                    vslib.slogger.warning(f'cam{index} read fail!!!')
                cams.append(index)
                cap.release()

        return cams

    @staticmethod
    def get_cam_list_res(scan_count: int = 10):
        """
        get valid camera list with supported resolutions
        [NOTE] cap.set will spend long time...

        Parameters
        ----------
        scan_count : int
            how many cameras to scan

        Returns
        -------
        dict
            valid camera dict with resolutions
        """

        cams = {}
        for index in range(scan_count):
            cap = cv2.VideoCapture(index)
            if cap and cap.isOpened():
                # don't read here to avoid cap.set fail!!!
                # if not cap.read()[0]:
                #     vslib.slogger.warning(f'cam{index} read fail!!!')

                """
                find default resolution
                """
                default_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                default_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                default_res = f'{default_w}x{default_h}'
                vslib.slogger.info(f'cam{index} default_res: {default_res}')

                """
                prepare resolutions
                """
                resolutions = medialib.DICT_RESOLUTIONS.copy()

                """
                remove unsupported resolution
                """
                for res in medialib.DICT_RESOLUTIONS:
                    (w, h) = (medialib.DICT_RESOLUTIONS[res]['w'], medialib.DICT_RESOLUTIONS[res]['h'])
                    ret_w = cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
                    ret_h = cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
                    if not ret_w or not ret_h:
                        # remove unsupported resolution
                        resolutions.pop(res)
                        continue

                    w_get = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    h_get = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    if w != w_get or h != h_get:
                        # remove unsupported resolution
                        resolutions.pop(res)

                if default_res in resolutions:
                    resolutions[default_res]['default'] = True
                cams[index] = resolutions

            cap.release()

        return cams
    # endregion [function]

    # region [with]
    def __enter__(self):
        self.logger.info()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.logger.info()
        self.release()
    # endregion [with]


def main():
    """
    For console test
    """
    import datetime

    # camera
    with vslib() as vs:
        if not vs.is_opened():
            print(f'open source {vs.src} fail!!!')
        else:
            vs.start()
            while True:
                # get frame (calculate time diff)
                time_start = datetime.datetime.now()
                frame = vs.read()
                time_end = datetime.datetime.now()
                print(f'vs.read() time: {(time_end - time_start).total_seconds() * 1000 : 0.3f} ms')
                # display
                cv2.imshow('webcam', frame)
                # wait for ESC key
                if cv2.waitKey(1) & 0xFF == 27:
                    break

            # Number of frames to capture
            num_frames = 120
            # start time
            start = datetime.datetime.now()
            # grab frames
            for i in range(0, num_frames):
                frame = vs.read()
            # end time
            end = datetime.datetime.now()
            # time elapsed
            seconds = (end - start).total_seconds()
            # fps
            fps = num_frames / seconds
            print(f'fps: {fps : 0.3f}')

            vs.stop()
            cv2.destroyAllWindows()

    # video
    # http://devimages.apple.com.edgekey.net/streaming/examples/bipbop_4x3/gear2/prog_index.m3u8
    with vslib(src='../asset/4K.mp4') as vs:
        if not vs.is_opened():
            print(f'open source {vs.src} fail!!!')
        else:
            _, _, fps, fcnt = vs.getinfo()
            delay = int(1000 / fps)
            print(f'delay: {delay} ms')
            print(f'video duration: {delay * fcnt} ms')
            while vs.grabbed:
                # NOTE!!!set pos_frames will take around 70~140ms
                # set frame position
                # vs.set(cv2.CAP_PROP_POS_FRAMES, i)

                # get frame (calculate time diff)
                time_start = datetime.datetime.now()
                frame = vs._read()
                time_end = datetime.datetime.now()
                print(f'vs._read() time: {(time_end - time_start).total_seconds() * 1000 : 0.3f} ms')
                if not vs.grabbed:
                    break
                # display
                cv2.imshow('video', frame)
                # wait for ESC key
                if cv2.waitKey(delay) & 0xFF == 27:
                    break
            cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
