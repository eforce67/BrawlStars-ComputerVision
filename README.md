**Brawl Stars AI Project**
==============================

**Project Overview**
-------------------

This Brawl Stars AI project aims to develop a continuous-time recurrent neural network made using neuroevolution to create a model that can efficiently play the popular FPS game, Brawl Stars. This project leverages various libraries and technologies to achieve its goal. Learn more about the project via the [wiki](https://github.com/eforce67/BrawlStars-ComputerVision/wiki) 
- Here's the computer vision model trained with 207 manually labeled images: [dataset](https://universe.roboflow.com/neonsharp/bs-multi-object-detection). Training results can be found here:
- [training result previous (not recommended)](https://mega.nz/folder/uCYmBaxJ#5FBihJ77fwlSB0rIlB70qw)
- [training result 2 (latest)](https://mega.nz/folder/uGogBbZB#hWY8tXO0kOGGrGU5vGityw)

**Getting Started**
---------------

To run the project, ensure you have the following libraries installed:

```bash
pip install graphviz matplotlib neat-python numpy opencv-python pillow pywin32 pynput ultralytics pyyaml
```
To start the program, I suggest you run train.py first to start training your first neural network. If you already have a model from a generation that you want to load from, in settings.yaml set load_training to your model path folder location.

**Input and Output Nodes**
-------------------------

### Input Nodes (18 total)

The input nodes consist of the following information that will be given to the model:

* `0`: Victory status 0 = None 1 = True
* `1`: Defeat status 0 = None 1 = True
* `2`: Draw status 0 = None 1 = True
* `3`: Respawn status 0 = None 1 = True
* `4`: Shot success 0 = None 1 = True
* `5`: Damage taken 0 = None 1 = True
* `6`: Nearest visible enemy 0 = None 1 = enemy distance
* `7`: Super ability status 0 = None 1 = True
* `8`: Hypercharge status 0 = None 1 = True
* `9`: Gadget status 0 = None 1 = True
* `10-17`: Closest 8 walls to the player (These inputs might be removed in the future due to frequent changes by Supercell. Ideally, the AI model should learn the map even without computer vision capabilities.)

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
* Manual-aim
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
- [x] Add manual aim logic
- [ ] Improve enemy and gem detection 
- [x] Parallel Training added
- [x] Configuration added for more customization  
