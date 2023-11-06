import argparse
import os
import shutil
import joblib
import glob

from vidio.read import VideoReader
from vidio.write import VideoWriter

def separate_deg_wrapper(video, dest):

    os.makedirs(os.path.dirname(dest), exist_ok=True)
    
    label_files=glob.glob(os.path.join(os.path.dirname(video), "*_labels.csv"))
    if len(label_files)==1:
        label_file=label_files[0]
        dest_folder=os.path.dirname(dest)
        shutil.copy(label_file, dest_folder)
    elif len(label_files) == 0:
        pass
    else:
        raise ValueError("More than one label file found")

    return separate(video, dest)

# def separate_sleap_wrapper(video, dest, **kwargs):

#     key, extension=os.path.splitext(os.path.basename(dest))
#     intermediate=os.path.join(
#         os.path.dirname(video),
#         key,
#         f"{key}{extension}",
#     )
#     os.makedirs(os.path.dirname(intermediate), exist_ok=True)
#     shutil.copy(video,intermediate)
#     separate(intermediate, dest, **kwargs)

def separate_sleap_wrapper(video, dest, **kwargs):

    os.makedirs(os.path.dirname(dest), exist_ok=True)
    separate(video, dest, **kwargs)

def separate(video, dest, **kwargs):

    video=VideoReader(filename=video)
    if kwargs:
        video.load_roi(**kwargs)
    else:
        lid=int(os.path.splitext(dest)[0].split("_")[-1])

        roi=lid
        rois={lid: (50+(200*(lid-1)), 50, 100, 100)}
        video.load_roi(roi=roi, rois=rois)

    fps=int(video.file_object.get(5))
    width=int(video.roi[2])
    height=int(video.roi[3])
    codec="MJPG"
    video_writer=VideoWriter(filename=dest, movie_format="opencv", codec=codec, width=width, height=height, fps=fps)
    for frame in video:
        video_writer.write(frame)

    video_writer.close()


def get_parser():

    ap=argparse.ArgumentParser()
    ap.add_argument("--videos", required=True)
    ap.add_argument("--destinations", required=True)
    ap.add_argument("--n-jobs", default=1)
    return ap


def process_all_videos(videos, destinations, n_jobs, f=separate, **kwargs):
    joblib.Parallel(n_jobs)(
            joblib.delayed(f)(
                video, dest, **kwargs
            ) for video, dest in zip(videos, destinations)
        )

def main():

    ap = get_parser()
    args = ap.parse_args()

    process_all_videos(args.videos, args.destinations, args.n_jobs)
