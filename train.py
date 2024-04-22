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
    results = net.predict(image_path, conf=0.60)
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
        
        # convert the bbox detect into distance using xcenter and ycenter
        coord = convert_box_to_coordinates(box.numpy().xywh)
        detected_objects.append({class_name: {'center': coord, 'area': (float(coord[2]), float(coord[3]))}})
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
    
def line_intersects_rect(p1_x, p1_y, p2_x, p2_y, rect_x, rect_y, rect_w, rect_h):
    """
    Checks if the line segment from (p1_x, p1_y) to (p2_x, p2_y) intersects with the rectangular area defined by (rect_x, rect_y), width (rect_w), and height (rect_h).

    Args:
        p1_x (float): The x-coordinate of the first point (player position).
        p1_y (float): The y-coordinate of the first point (player position).
        p2_x (float): The x-coordinate of the second point (enemy position).
        p2_y (float): The y-coordinate of the second point (enemy position).
        rect_x (float): The x-coordinate of the top-left corner of the rectangle (wall).
        rect_y (float): The y-coordinate of the top-left corner of the rectangle (wall).
        rect_w (float): The width of the rectangle (wall).
        rect_h (float): The height of the rectangle (wall).

    Returns:
        bool: True if the line segment intersects with the rectangular area, False otherwise.
    """
    # Check if the line segment is outside the rectangle's bounding box
    if (p1_x < rect_x and p2_x < rect_x) or (p1_x > rect_x + rect_w and p2_x > rect_x + rect_w) or (p1_y < rect_y and p2_y < rect_y) or (p1_y > rect_y + rect_h and p2_y > rect_y + rect_h):
        return False

    # Check if the line segment intersects with any of the rectangle's edges
    if intersect(p1_x, p1_y, p2_x, p2_y, rect_x, rect_y, rect_x + rect_w, rect_y):
        return True
    if intersect(p1_x, p1_y, p2_x, p2_y, rect_x + rect_w, rect_y, rect_x + rect_w, rect_y + rect_h):
        return True
    if intersect(p1_x, p1_y, p2_x, p2_y, rect_x + rect_w, rect_y + rect_h, rect_x, rect_y + rect_h):
        return True
    if intersect(p1_x, p1_y, p2_x, p2_y, rect_x, rect_y + rect_h, rect_x, rect_y):
        return True

    return False

def intersect(a1, a2, b1, b2, c1, c2, d1, d2):
    """
    Checks if the line segments (a1, a2) to (b1, b2) and (c1, c2) to (d1, d2) intersect.
    Implementation based on the Intersection of Two Lines algorithm from:
    https://www.geeksforgeeks.org/check-if-two-given-line-segments-intersect/
    """
    # Calculate the direction vectors for the two line segments
    q1 = (b1 - a1, b2 - a2)
    q2 = (d1 - c1, d2 - c2)

    # Calculate the cross product of the direction vectors
    cross = q1[0] * q2[1] - q1[1] * q2[0]

    # Check if the line segments are parallel or collinear
    if cross == 0:
        return False

    # Calculate the intersection point
    s = (q2[1] * (c1 - a1) - q2[0] * (c2 - a2)) / cross
    t = (q1[1] * (a1 - c1) - q1[0] * (a2 - c2)) / cross

    # Check if the intersection point lies on both line segments
    return 0 <= s <= 1 and 0 <= t <= 1

def clean_inputs(predictions):
    """
    Organizes the input layer using the objects detected and calculates distances
    from the player to all visible walls, enemies, and gems.
    """
    player_pos = next((obj['player_position'] for obj in predictions if 'player_position' in obj), None)
    player_bar = next((obj['player_health_bar'] for obj in predictions if 'player_health_bar' in obj), None)
    if player_pos and player_bar is None:
        player_coord = player_pos
    elif player_pos and player_bar is not None:
        player_coord = player_pos  # prefer player position over healthbar
    elif player_pos is None and player_bar is not None:
        player_coord = player_bar
    else:
        player_coord = None
    
    victory = [0]
    defeat = [0]
    draw = [0]
    respawning = [0]
    
    enemies = []
    hypercharge = [0]
    super_ability = [0]
    gadget = [0]
    walls = []
    gems = []
    input_keys = ["enemy_health_bar", "enemy_position", "wall", "gem", "gadget", "super", "hypercharge", "respawning"]

    for key in input_keys:
        try:
            for obj1 in predictions:
                if key in obj1:
                    match key:
                        case 'victory':
                            victory = [1]
                        case 'defeat':
                            defeat = [1]
                        case 'draw':
                            draw = [1]
                        case 'respawning':
                            respawning = [1]
                        case 'wall':
                            walls.append(obj1[key])
                        case 'gem':
                            gems.append(obj1[key]['center'])
                        case 'enemy_position' | 'enemy_health_bar':
                            enemies.append(obj1[key]['center'])
                        case 'hypercharge':
                            hypercharge = [1]
                        case 'super':
                            super_ability = [1]
                        case 'gadget':
                            gadget = [1]
        except TypeError:
            break

    # Calculate distances to visible walls, enemies, and gems
    visible_enemies = []
    visible_gems = []
    walls_in_range = []
    
    if player_coord is not None:
        p1_x, p1_y = player_coord['center'][2], player_coord['center'][3]
        for wall in walls:
            rect_x, rect_y = wall['center'][2], wall['center'][3]
            rect_w, rect_h = wall['area'][0], wall['area'][1]
            wall_distance = calculate_distance(p1_x, rect_x, p1_y, rect_y)
            walls_in_range.append(wall_distance)
            
            for enemy in enemies:
                enemy_x, enemy_y = enemy[0], enemy[1]
                if line_intersects_rect(p1_x, p1_y, enemy_x, enemy_y, rect_x, rect_y, rect_w, rect_h) is False:
                    print('found enemy')
                    enemy_distance = calculate_distance(p1_x, enemy_x, p1_y, enemy_y)
                    visible_enemies.append(enemy_distance)
            for gem in gems:
                gem_x, gem_y = gem[0], gem[1]
                if line_intersects_rect(p1_x, p1_y, gem_x, gem_y, rect_x, rect_y, rect_w, rect_h) is False:
                    print('found gems')
                    gem_distance = calculate_distance(p1_x, gem_x, p1_y, gem_y)
                    visible_gems.append(gem_distance)
    if walls_in_range:
        closest_8_walls = sorted(walls_in_range + [0] * (8 - len(walls_in_range)))[:8]
    else:
        closest_8_walls = [0]*8

    if visible_enemies:
        nearest_visible_enemy = min(visible_enemies)
    else:
        nearest_visible_enemy = 0

    if visible_gems:
        nearest_visible_gem = min(visible_gems)
    else:
        nearest_visible_gem = 0
    if player_coord is None:
        return victory + defeat + draw + respawning + [0] + [0] + super_ability + hypercharge + gadget + closest_8_walls
    return victory + defeat + draw + respawning + [nearest_visible_enemy] + [nearest_visible_gem] + super_ability + hypercharge + gadget + closest_8_walls

def neat_reward_fitness(genome, reward_num):
    """
    Increases the fitness of a genome by a certain amount.

    Args:
        genome: The genome to increase the fitness of.
        reward_num (float): The amount to increase the fitness by. If you pass in a negative number, it will decrease the score!
    """
    genome.fitness += reward_num

def run_simulation(genome, config):
    start_time = time()
    time_limit = 210 # 3 minutes and 50 seconds
    skip_turn1 = 2
    skip_turn2 = 3
    previous_action = None
    thread = None
    network = neat.ctrnn.CTRNN.create(genome, config, 0.01)
    controller.press_game()

    while True:
        controller.screen_shot()
        prediction = load_image_and_detect('LDPlayer_screen.png')
        shot_success = False
        respawning = False
        gadget_presence = False
        super_presence = False
        hypercharge = False

        for obj in prediction:
            if obj == 'shot_success':
                shot_success = True
            elif obj == 'respawning':
                respawning = True
            elif obj == 'gadget':
                gadget_presence = True
            elif obj == 'super':
                super_presence = True
            elif obj == 'hypercharge':
                hypercharge = True
            elif obj == 'victory':
                print('GAME STATUS: victory, rewarding the agent')
                neat_reward_fitness(genome, 3)
                break
            elif obj == 'defeat':
                print('GAME STATUS: defeat, removing points from the agent')
                neat_reward_fitness(genome, -2)
                break
            elif obj == 'draw':
                print('GAME STATUS: draw, rewarding the agent for a well played')
                neat_reward_fitness(genome, 1)
                break

        nputs = clean_inputs(prediction)
        print('INPUTS: ', nputs)
        current_time = time()
        elapsed_time = current_time - start_time
        print('Time passed:', elapsed_time)
        output = network.advance(nputs, elapsed_time, elapsed_time)
        action_taken = np.argmax(output)

        if action_taken in [0, 1, 2, 3, 4]:
            if thread is None:
                thread = controller.start_action(action_taken)
            else:
                thread.stop()
                thread = controller.start_action(action_taken)
        else:
            controller.start_action(action_taken)

        if elapsed_time >= time_limit:
            break

        if shot_success and previous_action == 4 and skip_turn1 == 3:
            skip_turn1 =- 3
            print('rewarding the agent for shot success')
            neat_reward_fitness(genome, 1)
        elif previous_action == 4 and not shot_success:
            skip_turn1 += 1
            print('removing a reward from the agent for setting ammo')
            neat_reward_fitness(genome, -0.35)
        else:
            skip_turn1 += 1
            print('reward cool down for shot success triggered')

        if not gadget_presence and action_taken == 5:
            print('removing a reward from the agent for setting unavailable gadget')
            neat_reward_fitness(genome, -0.35)

        if not super_presence and action_taken == 6:
            print('removing a reward from the agent for setting unavailable super')
            neat_reward_fitness(genome, -0.35)

        if not hypercharge and action_taken == 7:
            print('removing a reward from the agent for setting unavailable hypercharge')
            neat_reward_fitness(genome, -0.35)

        if respawning:
            if skip_turn2 == 3:
                skip_turn2 -= 3
                print('removing a reward from the agent for dying')
                neat_reward_fitness(genome, -0.45)
            else:
                skip_turn2 += 1
        
        previous_action = action_taken

    print('simulation ended...')
    thread.stop()
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
    neat_run(config_file='resources/config/neat_settings.txt')
