import os
import subprocess

for i in range(1,4):
    if i==2:
        continue
    else:
        subprocess.run("ffmpeg -i {}.flv -c:v libx264 -c:a mp3 {}.mp4".format(i+9,i))
        os.remove("{}.flv".format(i+9))
       