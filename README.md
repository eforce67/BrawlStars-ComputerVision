**Brawl Stars AI Project**
==============================

**Project Overview**
-------------------

The Brawl Stars AI project aims to develop a continuous-time recurrent neural network using neuroevolution to create an efficient gameplay strategy for the popular FPS game, Brawl Stars. This project leverages various libraries and technologies to achieve its goal.

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

* `0`: Respawn status
* `1`: Nearest visible enemy
* `2`: Nearest visible gem
* `3`: Super ability status
* `4`: Hypercharge status
* `5`: Gadget status
* `6-14`: Closest 8 walls to the player

**Demo**
--------

Here's a demo representing objects near the player:

![Demo of Player range and enemy detection](https://github.com/eforce67/BrawlStars-ComputerVision/blob/main/Figure_1.png)

### Output Nodes

The output nodes represent possible actions the AI agent can take:

* Move up
* Move down
* Move left
* Move right
* Auto aim
* Activate gadget
* Activate super
* Activate hypercharge

**Object Detection using YOLOv8**
--------------------------------

The project utilizes YOLOv8, a state-of-the-art object detection model by Ultralytics, to detect objects in the Brawl Stars environment. The following objects are supported by the fine-tuned YOLOv8 model:

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
