import pickle
from time import time

import neat
import numpy as np

import controller
from train import clean_inputs, load_image_and_detect

# Dictionary to map action indices to corresponding functions
ACTIONS = {
    0: controller.move_up,
    1: controller.move_down,
    2: controller.move_left,
    3: controller.move_right,
    4: controller.auto_aim,
    5: controller.activate_gadget,
    6: controller.activate_super,
    7: controller.activate_hypercharge,
}

def load_model(model_path, config_path):
    """
    Load the trained model and configuration.

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

def run_model(genome, config):
    """
    Run the trained model on the game.

    Args:
        genome: The trained genome.
        config: The configuration for the NEAT algorithm.
    """
    start_time = time()
    time_limit = 207  # 3 minutes and 45 seconds

    # Create the neural network from the genome and configuration
    network = neat.ctrnn.CTRNN.create(genome, config, 0.01)

    while True:
        controller.screen_shot()
        prediction = load_image_and_detect('LDPlayer_screen.png')
        inputs = clean_inputs(prediction)
        current_time = time()
        elapsed_time = current_time - start_time

        # Advance the neural network and get the output
        output = network.advance(inputs, current_time, current_time)
        action_taken = np.argmax(output)

        # Execute the action based on the output
        ACTIONS[action_taken]()

        # Exit the game if the time limit is reached
        if elapsed_time >= time_limit:
            print("3 minutes & 45 seconds have elapsed.")
            controller.exit_screen()
            break

if __name__ == '__main__':
    model, config = load_model('best.pickle', 'resources/config/neat_settings.txt')
    run_model(model, config)
