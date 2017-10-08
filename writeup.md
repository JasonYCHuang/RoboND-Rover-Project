## Project: Search and Sample Return

[//]: # (Image References)

[img_rock_color_thresh]: ./writeup_img/rock_color_thresh.png
[img_color_thresh]: ./writeup_img/color_thresh.png
[img_notebook_analysis]: ./writeup_img/notebook_analysis.png
[img_autonomous]: ./writeup_img/img_autonomous.png

---

### 1. Notebook Analysis

#### 1.1 Rock samples identification.

Rock samples that we are interested in are yellow color. I use color threshold to get rock pixels. This is implemented in a `rock_color_thresh` function, and pixels (R > 110, G > 110, B < 50) are considered as rock samples and are set to 1; other pixels are set to zero. As a result, the `rock_color_thresh` function outputs a binary image. The following image is an example.

![alt text][img_rock_color_thresh]

#### 1.2 Obstacle identification.

In images, obstacle is dark while territory is bright. A `color_thresh` function regards bright pixels (R, G and B are larger than 160) as territory. For obstacle pixels, it is just the inverse of territory. Moreover, I adopt `mask` to remove redundant area contributed by a perspective transformation.

From left to right in following images are territory, obstacle and rock after a perspective transformation.

![alt text][img_color_thresh]

#### 1.3 `process_image()`

Objects size in camera images is related to depth. Objects far away from a camera is smaller than those close to the camera. It is difficult to deduce locations without additional depth data in our configuration. To solve this, base on a top view(a bird view), we know object positions on a specifice plane.

Therefore, a mapping of four corners on a plane from a camera image to a top view is defined as `source` and `destination`, and we can get `perspect_transform`. With this transformation, we can get top views for each camera images.

To apply proper scale, and transform to a world coordinate, I use `rover_coords` and `pix_to_world` which are rotation and translation transformations. Image pixels of the world coordinate are then added into `worldmap` with different RGB colors meaning territory, obstacle or rock.

Finally, `worldmap` is integrated as a mosaic image.

Here is the result of Notebook analysis.

![alt text][img_notebook_analysis]

---

### 2. Autonomous Navigation

#### 2.1 `perception.py`

The code in `perception.py` is bascally the same in the __Notebook Analysis__.

A perspective transformation maps one plane from a 3D real world to camera images. Our rover suffers pitch and roll as driving over rock, or obstacle. Sudden brake or steep acceleration also lead to pitch or roll changes. In this circumstance, a mapping from territory to camera images is no longer the same as the original calibrated transformation. I filter images when pitch or roll is too high in `code/perception.py` `line 139-145`. With this, I can increase the fidelity around 10%.

This setup is good in this project, but may not be suitable for a real world case, since the territory is likely to not always be on the same plane. 

#### 2.2 `decision.py`

In `code/decision.py`, first, I move all mode actions to independent functions for easier code understanding.

##### 2.2.1 find rock

When rock pixels(yellow color) show in a image, the mode is switched to `find_rock`. `mode_approach_rock` handles action, and steers toward the rock. When `near_sample` is true, `mode_near_rock` stops the Rover, and pick up the sample with `mode_pick_up`.

##### 2.2.2 resolve stuck

From time to time, the Rover may stuck in rock or obstacle. `update_stuck_status` checks whether the Rover is `forward` or `find_rock` and under `Rover.stuck_vel` velocity. If this is `true`, the counter accumulates. After the counter reaches limit which means the Rover stuck for a while, it stops and starts to turn back in `mode_encounter_stuck`. Once the velocity goes over the limit (means it is moving again.), the mode is changed to `forward`. Otherwise, the Rover is still stuck and we ask the Rover to continue to turn back, and try to find a way out.

Here is a result (Resolution = 800 x 600, Graphics quality = good, FPS ~ 30)

![alt text][img_autonomous]

---

### 3. Future work

1. Sometimes the Rover continues to loop in a local area. It needs further decision to explore unknow area.




