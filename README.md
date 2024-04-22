**Brawl Stars AI Project**
==============================

**Project Overview**
-------------------

The Brawl Stars AI project aims to develop a continuous-time recurrent neural network using neuroevolution to create an efficient gameplay strategy for the popular FPS game, Brawl Stars. This project leverages various libraries and technologies to achieve its goal.
- Here's the computer vision model trained with 207 manually labeled images: [dataset](https://universe.roboflow.com/neonsharp/bs-multi-object-detection). Training results can be found here:
- [training result previous (not recommended)](https://mega.nz/folder/uCYmBaxJ#5FBihJ77fwlSB0rIlB70qw)
- [training result 2 (latest)(https://mega.nz/folder/uGogBbZB#hWY8tXO0kOGGrGU5vGityw)

**Getting Started**
---------------

To run the project, ensure you have the following libraries installed:

```bash
pip install graphviz matplotlib neat-python numpy opencv-python pillow pywin32 pynput ultralytics
```

**Input and Output Nodes**
-------------------------

### Input Nodes

The input nodes consist of the following information that will be given to the model:

* `0`: Victory status
* `1`: Defeat status
* `2`: Draw status
* `3`: Respawn status
* `4`: Nearest visible enemy
* `5`: Nearest visible gem
* `6`: Super ability status
* `7`: Hypercharge status
* `8`: Gadget status
* `9-17`: Closest 8 walls to the player

**Demo**
--------

Here's a demo representing objects near the player:

![Demo of Player range and enemy detection](https://github.com/eforce67/BrawlStars-ComputerVision/blob/main/Figure_1.png)
The script currently draws a line from the player to objects like enemies, gems, and walls. In special cases like the enemy and gem, if a line drawn from the player straight to the enemy intersects a rectangle/square-shaped wall, the intersect function will return false true, meaning we shouldn't shoot or walk straight towards the wall.
### Output Nodes

The output nodes represent possible actions the AI agent can take:

* Move up
* Move down
* Move left
* Move right
* Auto-aim
* Activate gadget
* Activate super
* Activate hypercharge

**Object Detection using YOLOv8**
--------------------------------

The project utilizes YOLOv8, a state-of-the-art object detection model by Ultralytics, to detect objects in the Brawl Stars environment. The fine-tuned YOLOv8 model supports the following objects:

* Player health bar
* Player position
* Teammate health bar
* Teammate position
* Enemy health bar
* Enemy position
* Damage taken
* Wall
* Ball
* Gem
* Ammo
* Gadget
* Super
* Hypercharge
* Shot success
* Respawn status
* victory status
* defeat status
* draw status

### TODO LIST
- [ ] Improve the computer vision model
- [ ] Improve simulation once the computer vision model is improved
- [ ] Improve neural network inputs once the computer vision model is improved
- [ ] Add manual aim logic
- [ ] Improve enemy and gem detection
