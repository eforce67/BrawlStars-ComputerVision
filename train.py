"""
Based on Darwinian evolutionary theory!
This script is in beta testing. The main focus is to train a neural network while having some computer vision to process the environment.
"""
import pickle
from time import time

import neat
import numpy as np
import torch
from ultralytics.models import YOLO

import controller
import visualize

class Point: 
    def __init__(self, x, y): 
        self.x = x 
        self.y = y 

class InputLayer:
    def __init__(self,
                 victory,
                 defeat,
                 draw,
                 respawning,
                 shot_success,
                 damage_taken,
                 visible_enemy,
                 super_ability,
                 gadget,
                 hypercharge,
                 closest_walls):
        self.victory = victory
        self.defeat = defeat
        self.draw = draw
        self.respawning = respawning
        self.shot_success = shot_success
        self.damage_taken = damage_taken
        self.visible_enemy = visible_enemy
        self.super_ability = super_ability
        self.gadget = gadget
        self.hypercharge = hypercharge
        self.closest_walls = closest_walls
        self.input_layer = [victory, defeat, draw, respawning, shot_success, damage_taken, visible_enemy, super_ability, gadget, hypercharge] + closest_walls

# Image processing functions
def load_image_and_detect(image_path, model='resources/models/best2.pt'):
    """
    Load an image and detect objects using YOLO.

    Args:
        image_path (str): Path to the image file.
        model (str): Path to the YOLO model file.

    Returns:
        list: A list of detected objects.
    """
    net = YOLO(model=model)
    if torch.cuda.is_available():
        net.cuda()
    else:
        net.cpu()
    results = net.predict(image_path, conf=0.60, save=True)
    return process_detection_results(results)

def process_detection_results(results):
    """
    Process the detection results.

    Args:
        results: The detection results.

    Returns:
        list: A list of detected objects with their classes and coordinates.
    """
    detected_objects = []
    for box in results[0].numpy().boxes:
        class_id = box.cls[0].astype(int) # get the class id
        class_name = results[0].numpy().names[class_id].lower() # get the class name using class id
        conversion = str(box.numpy().xywh).replace('[', '').replace(']', '').strip()
        parts = conversion.split()
        coord = tuple(float(part) for part in parts)
        coord = convert_box_to_coordinates(box.numpy().xywh)
        detected_objects.append({class_name: {'center': coord}})
    return detected_objects

def convert_box_to_coordinates(box):
    """
    Convert a bounding box to coordinates.

    Args:
        box: The bounding box.

    Returns:
        tuple: The coordinates of the bounding box.
    """
    conversion = str(box).replace('[', '').replace(']', '').strip()
    parts = conversion.split()
    return tuple(float(part) for part in parts)

def calculate_distance(x2, x1, y2, y1):
    """
    Calculate the distance between two points.

    Args:
        x2 (float): The x-coordinate of the second point.
        x1 (float): The x-coordinate of the first point.
        y2 (float): The y-coordinate of the second point.
        y1 (float): The y-coordinate of the first point.

    Returns:
        float: The distance between the two points.
    """
    return np.sqrt((np.square(x2 - x1)) + (np.square(y2 - y1)))

# taken from https://www.geeksforgeeks.org/check-if-two-given-line-segments-intersect/
def onSegment(p, q, r): 
    if ( (q.x <= max(p.x, r.x)) and (q.x >= min(p.x, r.x)) and 
           (q.y <= max(p.y, r.y)) and (q.y >= min(p.y, r.y))): 
        return True
    return False
  
def orientation(p, q, r): 
    # to find the orientation of an ordered triplet (p,q,r) 
    # function returns the following values: 
    # 0 : Collinear points 
    # 1 : Clockwise points 
    # 2 : Counterclockwise 
      
    # See https://www.geeksforgeeks.org/orientation-3-ordered-points/amp/  
    # for details of below formula.  
      
    val = (float(q.y - p.y) * (r.x - q.x)) - (float(q.x - p.x) * (r.y - q.y)) 
    if (val > 0): 
          
        # Clockwise orientation 
        return 1
    elif (val < 0): 
          
        # Counterclockwise orientation 
        return 2
    else: 
          
        # Collinear orientation 
        return 0
  
# The main function that returns true if  
# the line segment 'p1q1' and 'p2q2' intersect. 
def doIntersect(p1,q1,p2,q2): 
      
    # Find the 4 orientations required for  
    # the general and special cases 
    o1 = orientation(p1, q1, p2) 
    o2 = orientation(p1, q1, q2) 
    o3 = orientation(p2, q2, p1) 
    o4 = orientation(p2, q2, q1) 
  
    # General case 
    if ((o1 != o2) and (o3 != o4)): 
        return True
  
    # Special Cases 
  
    # p1 , q1 and p2 are collinear and p2 lies on segment p1q1 
    if ((o1 == 0) and onSegment(p1, p2, q1)): 
        return True
  
    # p1 , q1 and q2 are collinear and q2 lies on segment p1q1 
    if ((o2 == 0) and onSegment(p1, q2, q1)): 
        return True
  
    # p2 , q2 and p1 are collinear and p1 lies on segment p2q2 
    if ((o3 == 0) and onSegment(p2, p1, q2)): 
        return True
  
    # p2 , q2 and q1 are collinear and q1 lies on segment p2q2 
    if ((o4 == 0) and onSegment(p2, q1, q2)): 
        return True
  
    # If none of the cases 
    return False

def clean_inputs(predictions):
    """
    Organizes the input layer using the objects detected and calculates distances
    from the player to all visible walls, enemies, and gems.
    """
    player_coord = None
    
    for obj in predictions:
        if 'player_position' in obj:
            player_coord = obj['player_position']
            break
        elif 'player_health_bar' in obj:
            player_coord = obj['player_health_bar']

    victory, defeat, draw, respawning = 0, 0, 0, 0,
    hypercharge, super_ability, gadget = 0, 0, 0,
    shot_success, damage_taken = 0, 0,
    walls, enemies = [], []

    for obj in predictions:
        for key, value in obj.items():
            if key == 'victory':
                victory = 1
            elif key == 'defeat':
                defeat = 1
            elif key == 'draw':
                draw = 1
            elif key == 'respawning':
                respawning = 1
            elif key == 'shot_success':
                shot_success = 1
            elif key == 'damage_taken':
                damage_taken = 1
            elif key == 'wall':
                walls.append(value)
            elif key in ('enemy_position', 'enemy_health_bar'):
                enemies.append(value['center'])
            elif key == 'hypercharge':
                hypercharge = 1
            elif key == 'super':
                super_ability = 1
            elif key == 'gadget':
                gadget = 1

    walls_in_range = []
    available_enemies = []

    if enemies and player_coord != None:
        ppoint = Point(player_coord['center'][0], player_coord['center'][1])
        
        for enemy in enemies:
            epoint = Point(enemy[0], enemy[1])
            for wall in walls:
                x, y, w, h = wall['center']
                top_left = Point(x, y)
                top_right = Point(x + w, y)
                bottom_right = Point(x + w, y + h)
                bottom_left = Point(x, y + h)
                walls_in_range.append(calculate_distance(ppoint.x, x, ppoint.y, y))
                
                if not any(doIntersect(ppoint, point1, epoint, point2) for point1, point2 in [(top_left, bottom_left), (top_right, bottom_right), (bottom_left, bottom_right), (top_left, top_right)]):
                    available_enemies.append(round(calculate_distance(ppoint.x, epoint.x, ppoint.y, epoint.y), 5))
                    break
    closest_8_walls = sorted(list(set(walls_in_range)))[:8] if walls_in_range else [0] * 8
    nearest_visible_enemy = min(list(set(available_enemies))) if available_enemies else 0
    if player_coord is None:
        return InputLayer(victory, defeat, draw, respawning, shot_success, damage_taken, 0, super_ability, hypercharge, gadget, closest_8_walls)
    else:
        return InputLayer(victory, defeat, draw, respawning, shot_success, damage_taken, nearest_visible_enemy, super_ability, hypercharge, gadget, closest_8_walls)

def neat_reward_fitness(genome, reward_num):
    """
    Increases the fitness of a genome by a certain amount.

    Args:
        genome: The genome to increase the fitness of.
        reward_num (float): The amount to increase the fitness by. If you pass in a negative number, it will decrease the score!
    """
    genome.fitness += reward_num

def run_simulation(genome, config):
    def print_status(status):
        status_map = {
            'victory': (f'GAME STATUS: {status}, rewarding the agent', 3),
            'defeat': (f'GAME STATUS: {status}, removing points from the agent', -2),
            'draw': (f'GAME STATUS: {status}, rewarding the agent for a well played', 1)
        }
        print(status_map[status][0])
        neat_reward_fitness(genome, status_map[status][1])

    start_time = time()
    time_limit = 210  # 3 minutes and 30 seconds
    skip_turn1 = 2
    skip_turn2 = 3
    previous_action = None
    thread = None
    network = neat.ctrnn.CTRNN.create(genome, config, 0.01)
    controller.press_game()

    while True:
        controller.screen_shot()
        prediction = load_image_and_detect('LDPlayer_screen.png')
        nputs = clean_inputs(prediction)
        print('Inputs:', nputs.input_layer)
        if nputs.victory == 1:
            print_status('victory')
            break
        elif nputs.defeat == 1:
            print_status('defeat')
            break
        elif nputs.draw == 1:
            print_status('draw')
            break
        current_time = time()
        elapsed_time = current_time - start_time
        print('Time passed:', elapsed_time)
        output = network.advance(nputs.input_layer, elapsed_time, elapsed_time)
        action_taken = np.argmax(output)

        if action_taken in range(5):
            if thread is not None:
                thread.stop()
                thread = None
            thread = controller.start_action(action_taken)
        else:
            controller.start_action(action_taken)

        if elapsed_time >= time_limit:
            break

        if nputs.shot_success == 1 and previous_action in [4, 6, 7] and skip_turn1 == 3:
            skip_turn1 =- 3
            print('rewarding the agent for shot success')
            neat_reward_fitness(genome, 1)
        elif previous_action in [4, 6, 7] and nputs.shot_success == 0:
            skip_turn1 += 1
            print('removing a reward from the agent for setting ammo')
            neat_reward_fitness(genome, -0.35)
        else:
            if skip_turn1 == 3: pass
            else: skip_turn1 += 1

        if nputs.gadget == 1 and action_taken == 5:
            print('removing a reward from the agent for setting unavailable gadget')
            neat_reward_fitness(genome, -0.35)

        if nputs.super_ability == 0 and action_taken == 6:
            print('removing a reward from the agent for setting unavailable super')
            neat_reward_fitness(genome, -0.35)

        if nputs.hypercharge == 0 and action_taken == 7:
            print('removing a reward from the agent for setting unavailable hypercharge')
            neat_reward_fitness(genome, -0.35)

        if nputs.respawning == 1:
            if skip_turn2 == 3:
                skip_turn2 -= 3
                print('removing a reward from the agent for dying')
                neat_reward_fitness(genome, -0.45)
            else:
                if skip_turn2 == 3: pass
                else: skip_turn2 += 1
        
        previous_action = action_taken

    print('simulation ended...')
    if thread is not None: thread.stop()
    controller.press_game()

def survival_of_the_fittest(genomes, config):
    """
    Using natural selection to select the best genome(AI model)
    """
    for idx, (genome_id, genome) in enumerate(genomes):
        genome.fitness = 0
        run_simulation(genome, config)
    
def neat_run(config_file):
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_file)
    # start a population from stratch!
    pop = neat.Population(config)
    # load from a checkpoint if needed
    #pop = neat.Checkpointer.restore_checkpoint('neat-checkpoint-99')
    status = neat.StdOutReporter(True)
    pop.add_reporter(status)
    pop.add_reporter(neat.StatisticsReporter())
    pop.add_reporter(neat.Checkpointer(1))

    winner = pop.run(survival_of_the_fittest, 100)
    with open('best.pickle', 'wb') as f:
        pickle.dump(winner, f)
    
    # input layer names, input layers must be organized!
    nodes_name = {
        -9: 'activate gadget',
        -8: 'activate hypercharge',
        -7: 'activate super',
        -6: 'nearest gem',
        -5: 'nearest enemy',
        -4: 'respawning state',
        -3: 'draw status',
        -2: 'defeat status',
        -1: 'victory status',
        0: 'move up', 
        1: 'move down', 
        2: 'move left',
        3: 'move right',
        4: 'auto aim',
        5: 'activate gadget',
        6: 'activate super',
        7: 'activate hypercharge',
        }
    visualize.draw_net(config, winner, node_names=nodes_name, filename='resources/structure/Digraph.gv.svg')

if __name__ == '__main__':
    #neat_run(config_file='resources/config/neat_settings.txt')
    predict = load_image_and_detect('test2.png')
    nputs = clean_inputs(predict)
    print(nputs.input_layer)"""
Based on Darwinian evolutionary theory!
This script is in beta testing. The main focus is to train a neural network while having some computer vision to process the environment.
"""
import pickle
from time import time

import neat
import numpy as np
import torch
from ultralytics.models import YOLO

import controller
import visualize

class Point: 
    def __init__(self, x, y): 
        self.x = x 
        self.y = y 

class InputLayer:
    def __init__(self,
                 victory,
                 defeat,
                 draw,
                 respawning,
                 shot_success,
                 damage_taken,
                 visible_enemy,
                 super_ability,
                 gadget,
                 hypercharge,
                 closest_walls):
        self.victory = victory
        self.defeat = defeat
        self.draw = draw
        self.respawning = respawning
        self.shot_success = shot_success
        self.damage_taken = damage_taken
        self.visible_enemy = visible_enemy
        self.super_ability = super_ability
        self.gadget = gadget
        self.hypercharge = hypercharge
        self.closest_walls = closest_walls
        self.input_layer = [victory, defeat, draw, respawning, shot_success, damage_taken, visible_enemy, super_ability, gadget, hypercharge] + closest_walls

# Image processing functions
def load_image_and_detect(image_path, model='resources/models/best2.pt'):
    """
    Load an image and detect objects using YOLO.

    Args:
        image_path (str): Path to the image file.
        model (str): Path to the YOLO model file.

    Returns:
        list: A list of detected objects.
    """
    net = YOLO(model=model)
    if torch.cuda.is_available():
        net.cuda()
    else:
        net.cpu()
    results = net.predict(image_path, conf=0.60, save=True)
    return process_detection_results(results)

def process_detection_results(results):
    """
    Process the detection results.

    Args:
        results: The detection results.

    Returns:
        list: A list of detected objects with their classes and coordinates.
    """
    detected_objects = []
    for box in results[0].numpy().boxes:
        class_id = box.cls[0].astype(int) # get the class id
        class_name = results[0].numpy().names[class_id].lower() # get the class name using class id
        conversion = str(box.numpy().xywh).replace('[', '').replace(']', '').strip()
        parts = conversion.split()
        coord = tuple(float(part) for part in parts)
        coord = convert_box_to_coordinates(box.numpy().xywh)
        detected_objects.append({class_name: {'center': coord}})
    return detected_objects

def convert_box_to_coordinates(box):
    """
    Convert a bounding box to coordinates.

    Args:
        box: The bounding box.

    Returns:
        tuple: The coordinates of the bounding box.
    """
    conversion = str(box).replace('[', '').replace(']', '').strip()
    parts = conversion.split()
    return tuple(float(part) for part in parts)

def calculate_distance(x2, x1, y2, y1):
    """
    Calculate the distance between two points.

    Args:
        x2 (float): The x-coordinate of the second point.
        x1 (float): The x-coordinate of the first point.
        y2 (float): The y-coordinate of the second point.
        y1 (float): The y-coordinate of the first point.

    Returns:
        float: The distance between the two points.
    """
    return np.sqrt((np.square(x2 - x1)) + (np.square(y2 - y1)))

# taken from https://www.geeksforgeeks.org/check-if-two-given-line-segments-intersect/
def onSegment(p, q, r): 
    if ( (q.x <= max(p.x, r.x)) and (q.x >= min(p.x, r.x)) and 
           (q.y <= max(p.y, r.y)) and (q.y >= min(p.y, r.y))): 
        return True
    return False
  
def orientation(p, q, r): 
    # to find the orientation of an ordered triplet (p,q,r) 
    # function returns the following values: 
    # 0 : Collinear points 
    # 1 : Clockwise points 
    # 2 : Counterclockwise 
      
    # See https://www.geeksforgeeks.org/orientation-3-ordered-points/amp/  
    # for details of below formula.  
      
    val = (float(q.y - p.y) * (r.x - q.x)) - (float(q.x - p.x) * (r.y - q.y)) 
    if (val > 0): 
          
        # Clockwise orientation 
        return 1
    elif (val < 0): 
          
        # Counterclockwise orientation 
        return 2
    else: 
          
        # Collinear orientation 
        return 0
  
# The main function that returns true if  
# the line segment 'p1q1' and 'p2q2' intersect. 
def doIntersect(p1,q1,p2,q2): 
      
    # Find the 4 orientations required for  
    # the general and special cases 
    o1 = orientation(p1, q1, p2) 
    o2 = orientation(p1, q1, q2) 
    o3 = orientation(p2, q2, p1) 
    o4 = orientation(p2, q2, q1) 
  
    # General case 
    if ((o1 != o2) and (o3 != o4)): 
        return True
  
    # Special Cases 
  
    # p1 , q1 and p2 are collinear and p2 lies on segment p1q1 
    if ((o1 == 0) and onSegment(p1, p2, q1)): 
        return True
  
    # p1 , q1 and q2 are collinear and q2 lies on segment p1q1 
    if ((o2 == 0) and onSegment(p1, q2, q1)): 
        return True
  
    # p2 , q2 and p1 are collinear and p1 lies on segment p2q2 
    if ((o3 == 0) and onSegment(p2, p1, q2)): 
        return True
  
    # p2 , q2 and q1 are collinear and q1 lies on segment p2q2 
    if ((o4 == 0) and onSegment(p2, q1, q2)): 
        return True
  
    # If none of the cases 
    return False

def clean_inputs(predictions):
    """
    Organizes the input layer using the objects detected and calculates distances
    from the player to all visible walls, enemies, and gems.
    """
    player_coord = None
    
    for obj in predictions:
        if 'player_position' in obj:
            player_coord = obj['player_position']
            break
        elif 'player_health_bar' in obj:
            player_coord = obj['player_health_bar']

    victory, defeat, draw, respawning = 0, 0, 0, 0,
    hypercharge, super_ability, gadget = 0, 0, 0,
    shot_success, damage_taken = 0, 0,
    walls, enemies = [], []

    for obj in predictions:
        for key, value in obj.items():
            if key == 'victory':
                victory = 1
            elif key == 'defeat':
                defeat = 1
            elif key == 'draw':
                draw = 1
            elif key == 'respawning':
                respawning = 1
            elif key == 'shot_success':
                shot_success = 1
            elif key == 'damage_taken':
                damage_taken = 1
            elif key == 'wall':
                walls.append(value)
            elif key in ('enemy_position', 'enemy_health_bar'):
                enemies.append(value['center'])
            elif key == 'hypercharge':
                hypercharge = 1
            elif key == 'super':
                super_ability = 1
            elif key == 'gadget':
                gadget = 1

    walls_in_range = []
    available_enemies = []

    if enemies and player_coord != None:
        ppoint = Point(player_coord['center'][0], player_coord['center'][1])
        
        for enemy in enemies:
            epoint = Point(enemy[0], enemy[1])
            for wall in walls:
                x, y, w, h = wall['center']
                top_left = Point(x, y)
                top_right = Point(x + w, y)
                bottom_right = Point(x + w, y + h)
                bottom_left = Point(x, y + h)
                walls_in_range.append(calculate_distance(ppoint.x, x, ppoint.y, y))
                
                if not any(doIntersect(ppoint, point1, epoint, point2) for point1, point2 in [(top_left, bottom_left), (top_right, bottom_right), (bottom_left, bottom_right), (top_left, top_right)]):
                    available_enemies.append(round(calculate_distance(ppoint.x, epoint.x, ppoint.y, epoint.y), 5))
                    break
    closest_8_walls = sorted(list(set(walls_in_range)))[:8] if walls_in_range else [0] * 8
    nearest_visible_enemy = min(list(set(available_enemies))) if available_enemies else 0
    if player_coord is None:
        return InputLayer(victory, defeat, draw, respawning, shot_success, damage_taken, 0, super_ability, hypercharge, gadget, closest_8_walls)
    else:
        return InputLayer(victory, defeat, draw, respawning, shot_success, damage_taken, nearest_visible_enemy, super_ability, hypercharge, gadget, closest_8_walls)

def neat_reward_fitness(genome, reward_num):
    """
    Increases the fitness of a genome by a certain amount.

    Args:
        genome: The genome to increase the fitness of.
        reward_num (float): The amount to increase the fitness by. If you pass in a negative number, it will decrease the score!
    """
    genome.fitness += reward_num

def run_simulation(genome, config):
    def print_status(status):
        status_map = {
            'victory': (f'GAME STATUS: {status}, rewarding the agent', 3),
            'defeat': (f'GAME STATUS: {status}, removing points from the agent', -2),
            'draw': (f'GAME STATUS: {status}, rewarding the agent for a well played', 1)
        }
        print(status_map[status][0])
        neat_reward_fitness(genome, status_map[status][1])

    start_time = time()
    time_limit = 210  # 3 minutes and 30 seconds
    skip_turn1 = 2
    skip_turn2 = 3
    previous_action = None
    thread = None
    network = neat.ctrnn.CTRNN.create(genome, config, 0.01)
    controller.press_game()

    while True:
        controller.screen_shot()
        prediction = load_image_and_detect('LDPlayer_screen.png')
        nputs = clean_inputs(prediction)
        print('Inputs:', nputs.input_layer)
        if nputs.victory == 1:
            print_status('victory')
            break
        elif nputs.defeat == 1:
            print_status('defeat')
            break
        elif nputs.draw == 1:
            print_status('draw')
            break
        current_time = time()
        elapsed_time = current_time - start_time
        print('Time passed:', elapsed_time)
        output = network.advance(nputs.input_layer, elapsed_time, elapsed_time)
        action_taken = np.argmax(output)

        if action_taken in range(5):
            if thread is not None:
                thread.stop()
                thread = None
            thread = controller.start_action(action_taken)
        else:
            controller.start_action(action_taken)

        if elapsed_time >= time_limit:
            break

        if nputs.shot_success == 1 and previous_action in [4, 6, 7] and skip_turn1 == 3:
            skip_turn1 =- 3
            print('rewarding the agent for shot success')
            neat_reward_fitness(genome, 1)
        elif previous_action in [4, 6, 7] and nputs.shot_success == 0:
            skip_turn1 += 1
            print('removing a reward from the agent for setting ammo')
            neat_reward_fitness(genome, -0.35)
        else:
            if skip_turn1 == 3: pass
            else: skip_turn1 += 1

        if nputs.gadget == 1 and action_taken == 5:
            print('removing a reward from the agent for setting unavailable gadget')
            neat_reward_fitness(genome, -0.35)

        if nputs.super_ability == 0 and action_taken == 6:
            print('removing a reward from the agent for setting unavailable super')
            neat_reward_fitness(genome, -0.35)

        if nputs.hypercharge == 0 and action_taken == 7:
            print('removing a reward from the agent for setting unavailable hypercharge')
            neat_reward_fitness(genome, -0.35)

        if nputs.respawning == 1:
            if skip_turn2 == 3:
                skip_turn2 -= 3
                print('removing a reward from the agent for dying')
                neat_reward_fitness(genome, -0.45)
            else:
                if skip_turn2 == 3: pass
                else: skip_turn2 += 1
        
        previous_action = action_taken

    print('simulation ended...')
    if thread is not None: thread.stop()
    controller.press_game()

def survival_of_the_fittest(genomes, config):
    """
    Using natural selection to select the best genome(AI model)
    """
    for idx, (genome_id, genome) in enumerate(genomes):
        genome.fitness = 0
        run_simulation(genome, config)
    
def neat_run(config_file):
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_file)
    # start a population from stratch!
    pop = neat.Population(config)
    # load from a checkpoint if needed
    #pop = neat.Checkpointer.restore_checkpoint('neat-checkpoint-99')
    status = neat.StdOutReporter(True)
    pop.add_reporter(status)
    pop.add_reporter(neat.StatisticsReporter())
    pop.add_reporter(neat.Checkpointer(1))

    winner = pop.run(survival_of_the_fittest, 100)
    with open('best.pickle', 'wb') as f:
        pickle.dump(winner, f)
    
    # input layer names, input layers must be organized!
    nodes_name = {
        -9: 'activate gadget',
        -8: 'activate hypercharge',
        -7: 'activate super',
        -6: 'nearest gem',
        -5: 'nearest enemy',
        -4: 'respawning state',
        -3: 'draw status',
        -2: 'defeat status',
        -1: 'victory status',
        0: 'move up', 
        1: 'move down', 
        2: 'move left',
        3: 'move right',
        4: 'auto aim',
        5: 'activate gadget',
        6: 'activate super',
        7: 'activate hypercharge',
        }
    visualize.draw_net(config, winner, node_names=nodes_name, filename='resources/structure/Digraph.gv.svg')

if __name__ == '__main__':
    #neat_run(config_file='resources/config/neat_settings.txt')
    predict = load_image_and_detect('test2.png')
    nputs = clean_inputs(predict)
    print(nputs.input_layer)
