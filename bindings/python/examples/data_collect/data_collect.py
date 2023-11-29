#
# BSD 3-Clause License
#
# Copyright (c) 2019, Analog Devices, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
import aditofpython as tof
import argparse
import os 
import sys
import time
import numpy as np
import threading

mode_help_message = """Valid mode (-m) options are:
        0: short-range native;
        1: long-range native;
        2: short-range Qnative;
        3: long-range Qnative
        4: pcm-native;
        5: long-range mixed;
        6: short-range mixed
        
        Note: --m argument supports both index and string (0/sr-native) """


IP = '10.42.0.1'
FRAME_TYPES = ['raw', 'depth', 'ir', 'conf','metadata']

def fileWriterTask(**kwargs):
    file_name = f"{kwargs['pFolderPath']}/{kwargs['pFrameType']}_frame_{kwargs['pTimeBuffer']}_{str(kwargs['pLoopCount'])}.bin"
    with open(file_name, "wb") as file:
        bin_data = frame.getData(frame_type)
        file.write(bytearray(bin_data))
    if kwargs['pFrameType'] == 'depth':
        if kwargs['pLoopCount'] == 0:
            with open(f"{kwargs['pFolderPath']}raw_frame_{kwargs['pTimeBuffer']}.raw", "wb") as file:
                file.write((kwargs['pwidth'].to_bytes(4, byteorder='little', signed=False)))
                file.write((kwargs['pheight'].to_bytes(4, byteorder='little', signed=False)))
                file.write((kwargs['n_frames'].to_bytes(4, byteorder='little', signed=False)))
            
        with open(f"{kwargs['pFolderPath']}raw_frame_{kwargs['pTimeBuffer']}.raw", "ab") as file:
            file.write(frame.getData("ir"))
            file.write(frame.getData("depth"))
            file.write(frame.getData("xyz"))
            file.write(frame.getData("metadata"))
                
if __name__ == '__main__':
    parser = argparse.ArgumentParser( formatter_class=argparse.RawTextHelpFormatter,
        description='Script to run data collect executible')
    parser.add_argument(
        'config', help='path to the configuration file (with .json extension)')
    parser.add_argument('-f', dest='folder', default='./',
                        help='output folder')
    parser.add_argument('-n', dest='ncapture', type=int, default=1,
                        help='number of frame captured')
    parser.add_argument('-m', dest='mode',  default='sr-native',
                        help=mode_help_message)
    parser.add_argument('-wt', dest='warmup_time', type=int,
                        default=0, help='warmup time in seconds')
    parser.add_argument('--ccb', type=str, 
                        help='The path to store CCB content', metavar='<FILE>')                    
    parser.add_argument('--ip', default=IP, help='camera IP')
    parser.add_argument('-fw', dest='firmware', help='Adsd3500 firmware file')
    parser.add_argument('-ft', dest='frame_type', choices=FRAME_TYPES,
                        default='depth', help='FrameType of saved image')

    args = parser.parse_args()

    print ("SDK version: ", tof.getApiVersion(),"| branch: ", tof.getBranchVersion(), 
           "| commit: ", tof.getCommitVersion() )

    #check if directory output folder exist, if not, create one
    if (args.folder):
        if not os.path.isdir(args.folder):
            os.mkdir(args.folder)
            print("output folder created")

    print ("Output folder: ", args.folder)
    print ("Mode: ", args.mode )
    print ("Number of frames: ", args.ncapture)
    print ("Frame type is: ", args.frame_type)
    print ("Warm Up time is: ", args.warmup_time)
    print("Ip address is: ", args.ip)
   
    if (args.config):
        print ("Json file: ", args.config)
        
    if (args.firmware):
        print("Firmware file is: ", args.firmware)
    
    if (args.ccb):
        print("Path to store CCB content: " , args.ccb)

    try:
        system = tof.System()
    except:
        print("Failed to create system")

    cameras = []
    status = system.getCameraList(cameras, "ip:" + args.ip)
    print("system.getCameraList(): ", status)
    if status != tof.Status.Ok:
        sys.exit("No cameras found")
    
    camera1 = cameras[0]

    status = camera1.initialize(args.config)
    print('camera1.initialize()', status)
    if status != tof.Status.Ok:
        sys.exit("Could not initialize camera!")

    cam_details = tof.CameraDetails()
    status = camera1.getDetails(cam_details)
    print('camera1.getDetails()', status)

    print(f'Camera ID: {cam_details.cameraId}')
    
    print ('SD card image version: ', cam_details.sdCardImageVersion)
    print ("Kernel version: ", cam_details.kernelVersion)
    print ("U-Boot version: ", cam_details.uBootVersion)

    
    if (args.firmware):
        #status = camera1.adsd3500UpdateFirmware(args.firmware)
        if status != tof.Status.Ok:
            print('Could not update the Adsd3500 firmware')
        else:
            print('Please reboot the board')


    frame_types = []
    status = camera1.getAvailableFrameTypes(frame_types)
    if status != tof.Status.Ok or len(frame_types) == 0:
        sys.exit('Cound not aquire frame types')
    else:
        print(f'available frame_types: {frame_types}')
        
    mode_name = 'none'
    #Working on master. Needs changes based on aditofpytohn
    if (args.mode):
        try:
            args.mode = int(args.mode) # try to convert x to an int
            status = camera1.getFrameTypeNameFromId(args.mode, mode_name)
            if status[0] == tof.Status.Ok:
                mode_name = status[1]
                print(f'Mode: {mode_name}')
            else:
                sys.exit(f'Mode: {args.mode} is invalid for this type of camera')
        except ValueError:
            if args.mode not in frame_types:
                sys.exit(f'{args.mode} is not a valid mode')
            else:
                mode_name = args.mode
                print(f'Mode: {mode_name}')

    frame_type = args.frame_type
    
    #pcm-native contains ir only
    if frame_type != 'ir' and mode_name == 'pcm-native':
        print("Mode doesn't contain depth/conf/full-frame/metadata data, setting --ft ")
        print("(frameType) to ir.")
        frame_type = "ir";
    
    status = camera1.setFrameType(mode_name)
    if status != tof.Status.Ok:
        sys.exit("Could not set camera frame type!")
    
    status = camera1.adsd3500GetEnableMetadatainAB();
    enableMetadata = status[1]
    if not enableMetadata:
        sys.exit("Metadata is unvailable for this camera")
    
    timebuffer = time.strftime('%Y%m%d%H%M%S')

    if (args.ccb):
        status = camera1.saveModuleCCB(args.ccb)
        print("camera1.saveModuleCCB()", status)

    status = camera1.start()
    if status != tof.Status.Ok:
        sys.exit("Could not start camera!")
   
    frame = tof.Frame()
    frameDetails = tof.FrameDetails()
    
    warmup_start = time.monotonic()
    print(warmup_start)
    
    warmup_time = args.warmup_time
    #Wait until the warmup time is finished
    if warmup_time > 0:
        while time.monotonic() - warmup_start < warmup_time:
            #Request a frame from the camera object
            status = camera1.requestFrame(frame)
            if status != tof.Status.Ok:
                sys.exit("Could not request frame!")

    frame_size = 0;
    print(f'Rquesting {args.ncapture} frames!')
    
    #start high resolution timer
    start_time = time.perf_counter_ns()
    
    #Request the frames for the respective mode
    for loopcount in range(args.ncapture):
        status = camera1.requestFrame(frame)
        if status != tof.Status.Ok:
            sys.exit("Could not request frame!")
        frame.getDetails(frameDetails);
        height = frameDetails.height;
        width = frameDetails.width;

        frameDataDetails = tof.FrameDataDetails()
        #Depth Data
        if frame_type == "depth":
            status = frame.getDataDetails("depth", frameDataDetails)
            if status != tof.Status.Ok:
                sys.exit("Depth disabled from ini file!")
            status = frame.getDataDetails("ir", frameDataDetails)
            if status != tof.Status.Ok:
                sys.exit("ir disabled from ini file!")   
            status = frame.getDataDetails("xyz", frameDataDetails)
            if status != tof.Status.Ok:
                sys.exit("xyz disabled from ini file!")  
            status = frame.getDataDetails("metadata", frameDataDetails)
            if status != tof.Status.Ok:
                sys.exit("metadata disabled from ini file!")                   
            
        #IR data
        elif frame_type == "ir":
            if mode_name != "pcm-native":
                status = frame.getDataDetails(frame_type, frameDataDetails)
                if status != tof.Status.Ok:
                    sys.exit("IR disabled from ini file!")
            frame_size = frameDataDetails.bytesCount
        
        #Conf data
        elif frame_type == "conf" :
            status = frame.getDataDetails(frame_type, frameDataDetails)
            if status != tof.Status.Ok:
                sys.exit("conf disabled from ini file!")
            frame_size = frameDataDetails.bytesCount
            
        #Metadata
        elif frame_type == "metadata":
            status = frame.getDataDetails(frame_type, frameDataDetails)
            frame_size = frameDataDetails.bytesCount
        
        else:
            print("Can't recognize frame data type!")
        
        metadata = tof.Metadata
        status, metadata = frame.getMetadataStruct()

        print("frame:", loopcount)
        print("Sensor temperature from metadata: ", metadata.sensorTemperature)
        print("Laser temperature from metadata: ", metadata.laserTemperature)
        print("Frame number from metadata: ", metadata.frameNumber)
        print("Mode from metadata: ", metadata.imagerMode)
        
        params = {'pFolderPath': args.folder, 'pFrameType': frame_type, 'n_frames': args.ncapture,
        'pTimeBuffer': timebuffer, 'pLoopCount': loopcount, 'pwidth':width, 'pheight':height}
        t = threading.Thread(target=fileWriterTask, kwargs=params)  
        
        # Start the thread
        t.start()

        # Wait for the thread to finish
        t.join()
        
    end_time = time.perf_counter_ns()
    total_time = (end_time - start_time) / 1e9;
    
    if total_time > 0:
        measured_fps = args.ncapture / total_time
        print("Measured FPS: ", format(measured_fps, '.5f'))
        
    status = camera1.stop()
    if status != tof.Status.Ok:
        sys.exit("Error stopping camera!")
        

