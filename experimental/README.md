# Experiments

This is a bit of a "dumping ground" for reference of other things I experimented with while developing these utilities.

I discovered that `Wand` with `ImageMagick` resulted in the most consistent performance.

Then I realized that the file IO was probably dominating the experiments.
So I'll have to fix that first by caching the open files and run more experiments.

`OpenCV` with `numpy` may be a faster option, but there is no "native" solution for compositing alpha images
(only compositing alpha layers vi blending values) so I will have to do a bit more work to run that experiment.

I plan to study this issue thread and experiment at some point:
https://github.com/opencv/opencv/issues/20780
