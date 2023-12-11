
import csv
import os
import threading
import time
import uuid
from typing import Any, Optional, TextIO

import numpy as np
from db_adaptor import DBAdaptor
from device import Device

from application_manager import ApplicationManager

join = os.path.join

class TxtDBAdaptor(DBAdaptor):
    def __init__(self, subscriber_id: Optional[str] = None) -> None:
        self._recording = False
        self._output_dir = './txt_recorder_out/'
        self._original_output_dir = self._output_dir
        self._recorder_thread = None

        self._subscriptions: set[tuple[Device, str]] = set()
        if subscriber_id == None:
            self._sub_id = uuid.uuid4().hex
        else:
            self._sub_id = subscriber_id
    
    def __del__(self):
        """ensure thread is stopped when object is deleted, unsub all data"""
        self._recording = False
        if self._recorder_thread is not None:
            self._recorder_thread.join()
        self.clear_channels()

    def set_output_folder(self, folder: str):
        self._assert_not_recording()
        self._output_dir = folder
        self._original_output_dir = folder

    def add_channel(self, device: Device, channel: str):
        self._assert_not_recording()
        pair = (device, channel)
        self._subscriptions.add(pair)
        ApplicationManager.get_instance().subscribe_device_data(device, channel, self._sub_id)

    def remove_channel(self, device: Device, channel: str):
        self._assert_not_recording()
        pair = (device, channel)
        if pair in self._subscriptions:
            self._subscriptions.remove(pair)
            ApplicationManager.get_instance().unsubscribe_device_data(device, channel, self._sub_id)

    def clear_channels(self):
        self._assert_not_recording()
        ApplicationManager.get_instance().unsubscribe_all_device_data(self._sub_id)

    def get_channels(self) -> set[tuple[Device, str]]:
        return self._subscriptions.copy()

    def start_recording(self):
        if self._recording:
            print('start recording called twice, ignoring')
            return
        self._auto_create_rename_folder()
        self._recording = True
        self._recorder_thread = threading.Thread(target=self._recorder_thread_main)
        self._recorder_thread.start()

    def stop_recording(self):
        self._recording = False
        if self._recorder_thread is not None:
            self._recorder_thread.join()
    
    def is_recording(self) -> bool:
        return self._recording

    def _assert_not_recording(self):
        assert not self._recording, 'Cannot modify parameters when recording is on'

    def _auto_create_rename_folder(self):
        """if output dir not exist, create. If exist and has content, add a postfix to the dir"""
        i = 1
        while True:
            dir_conflicted = False

            if not os.path.exists(self._output_dir):
                os.mkdir(self._output_dir)
            elif os.path.isdir(self._output_dir):
                # check if dir is empty
                dir_content = os.listdir(self._output_dir)
                if len(dir_content) > 0:
                    # not empty, use another dir
                    dir_conflicted = True
            else:
                # is a file, use another dir
                dir_conflicted = True
            
            if dir_conflicted:
                # try find another dir
                i += 1
                self._output_dir = self._original_output_dir + f'_{i}'
            else:
                break

    def _recorder_thread_main(self):
        # clear previous data
        for device, channel in self._subscriptions:
            queue = ApplicationManager.get_instance().get_device_data_queue(device, channel, self._sub_id)
            while True:
                try:
                    queue.get_nowait()
                except:
                    break
        
        root_dir = os.path.abspath(self._output_dir)
        # create folder & csv writer for each channel
        sub_to_writer_dict: dict[tuple[Device, str], Any] = {}
        writers = []
        for device, channel in self._subscriptions:
            folder_name = f'{device.get_name()}.{channel}'
            full_folder_name = join(root_dir, folder_name)
            os.mkdir(full_folder_name)
            writer = SegmentedCSVWriter(full_folder_name)
            writers.append(writer)
            sub_to_writer_dict[(device, channel)] = writer
        
        # main loop
        while self._recording:
            time.sleep(0.1)
            for (device, channel), writer in sub_to_writer_dict.items():
                queue = ApplicationManager.get_instance().get_device_data_queue(device, channel, self._sub_id)
                all_xs = []
                all_ys = []
                while True:
                    try:
                        xs, ys = queue.get_nowait()
                        all_xs.append(xs)
                        all_ys.append(ys)
                    except:
                        break
                if len(all_xs) == 0 or len(all_ys) == 0:
                    continue
                concat_xs = np.concatenate(all_xs, axis=0)
                concat_ys = np.concatenate(all_ys, axis=0)
                writer.write(np.stack((concat_xs, concat_ys), 1))
        
        for writer in writers:
            writer.close()


class SegmentedCSVWriter:
    def __init__(self, dir: str, line_limit: int = 50000) -> None:
        self._directory = dir
        self._line_limit = line_limit
        self._count = 0

        self._file: Optional[TextIO] = None
        self._writer = None
        self._file_num = 0

        self._inc_file()

    def __del__(self):
        self.close()

    def write(self, array: np.ndarray):
        self._writer.writerows(array)
        lines = array.shape[0]
        self._count += lines
        if self._count >= self._line_limit:
            self._inc_file()
    
    def close(self):
        if self._file is not None:
            self._file.close()

    def _inc_file(self):
        if self._file is not None:
            self._file.close()
        self._file_num += 1
        self._file = open(join(self._directory, f'{self._file_num:0>4}.csv'), mode='wt', encoding='utf-8')
        self._writer = csv.writer(self._file)
        self._count = 0


if __name__ == '__main__':
    adaptor = TxtDBAdaptor()
