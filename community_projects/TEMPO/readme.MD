TEMPO
================================================================

Song generation based on heart rate

![Output example](./output.gif?raw=true)

Requirements
------------

- install [fluidsynth](https://www.fluidsynth.org/)>=2.0.0
- `pip install -r requirements.txt`

Supported Models
----------------

Usage
-----

1. Setup virtual environment
    - run `. setup_env.sh`
    - `cd community_projects/TEMPO`
    - `pip install -r requirements.txt`
    - `sudo chmod 777 download_files`
    - `./download_files.sh`
  
2. Run the web application
    - run `python app_hailo.py`

3. 


For more information:
```shell script
./detection_with_tracker.py -h
```
Example 
-------
**Command**
```shell script
./detection_with_tracker.py -i input_video.mp4 -o output_video.mp4 -l coco.txt -s 0.5
```

Additional Notes
----------------

- The example was only tested with ``HailoRT v4.18.0``
- The example expects a HEF which contains the HailoRT Postprocess
- The script assumes that the input video is in a standard format supported by OpenCV (e.g., .mp4, .avi).

Disclaimer
----------
This code example is provided by Hailo solely on an “AS IS” basis and “with all faults”. No responsibility or liability is accepted or shall be imposed upon Hailo regarding the accuracy, merchantability, completeness or suitability of the code example. Hailo shall not have any liability or responsibility for errors or omissions in, or any business decisions made by you in reliance on this code example or any part of it. If an error occurs when running this example, please open a ticket in the "Issues" tab.

This example was tested on specific versions and we can only guarantee the expected results using the exact version mentioned above on the exact environment. The example might work for other versions, other environment or other HEF file, but there is no guarantee that it will.