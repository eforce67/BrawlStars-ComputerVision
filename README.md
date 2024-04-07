# Brawl Stars AI Project

## Project Overview
The Brawl Stars AI project aims to develop a recurrent neural network using neuroevolution to create an efficient gameplay strategy for the popular FPS game, Brawl Stars. This project utilizes various libraries and technologies to achieve its goal.

## Requirements
To run the project, ensure you have the following libraries installed:
```
!pip install graphviz matplotlib neat-python numpy opencv-python pillow pywin32 pynput ultralytics
```

## Input & Output Nodes
### Input Nodes
Neat input nodes act as sensors to detect game environment variables. They include:
- Connecter_1-6: These sensors detect objects in the player's direction, divided into equal slices around the player's position.

### Here is a demo of this idea!
![Demo of Player range and enemy detection](https://github.com/eforce67/BrawlStars-ComputerVision/blob/main/Figure_1.png)

### Output Nodes
Output nodes represent possible actions the AI agent can take:
- Move_left
- Move_right
- Move_back
- Move_forward
- Stand_Still
- Auto_aim
- Manual_aim
- Activate Super
- Activate Hypercharge

## Using YOLOv8 for Object Detection
The project utilizes YOLOv8, a state-of-the-art object detection model by Ultralytic, to detect objects in the Brawl Stars environment. The following objects are supported by the fine-tuned YOLOv8 model:
- player_health_bar
- player_position
- teammate_health_bar
- teammate_position
- enemy_health_bar
- enemy_position
- damage_taken
- wall
- ball
- gem
- ammo
- gadget
- super
- hypercharge
- shot_success

These detected objects provide crucial details to enhance the AI's understanding of the game environment.
