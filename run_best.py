import pickle
from time import time

import neat
import numpy as np

import controller
from train import clean_inputs, load_image_and_detect


def load_model(model_path, config_path):
    """ Load the trained model and configuration.

    Args:
        model_path (str): Path to the saved model file.
        config_path (str): Path to the configuration file.

    Returns:
        tuple: Tuple containing the loaded model and configuration.
    """
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    config = neat.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )
    return model, config

def run_model(genome, config, emulator_name):
    """ Run the trained model on the game.

    Args:
        genome: The trained genome.
        config: The configuration for the NEAT algorithm.
    """
    # Create the neural network from the genome and configuration
    network = neat.ctrnn.CTRNN.create(genome, config, 0.01)
    control_instance = controller.ControllerInstance(emulator_name)
    control_instance.press_game()
    
    time_limit = 207
    thread = None
    start_time = time()

    while True:
        control_instance.screen_shot()
        prediction = load_image_and_detect(f'screen_{emulator_name}.png')
        inputs = clean_inputs(prediction)
        if (inputs.victory | inputs.defeat | inputs.draw) == 1:
            break

        current_time = time()
        elapsed_time = current_time - start_time

        # Advance the neural network and get the output
        output = network.advance(inputs.input_layer, current_time, current_time)
        action_taken = np.argmax(output)

        # Execute the action based on the output
        if action_taken in range(3):
            if thread is not None:
                thread.stop()
                thread = None
            thread = controller.start_action(action_taken, control_instance, inputs.visible_enemy, inputs.visible_enemy_epoint)
        else:
            controller.start_action(action_taken, control_instance, inputs.visible_enemy, inputs.visible_enemy_epoint)

        # Exit the game if the time limit is reached
        if elapsed_time >= time_limit:
            print("3 minutes & 45 seconds have elapsed.")
            break

    print('finished playing the game')
    if thread is not None: thread.stop()
    
if __name__ == '__main__':
    model, config = load_model('resources/structure/best.pickle', 'resources/config/neat_settings.txt')
    run_model(model, config, 'LDPlayer')
