import yaml

with open('resources/config/settings.yaml', 'r') as configuration_file:
    config = yaml.safe_load(configuration_file)

# bool constant
SOURCE_TRAINING = config.get('load_training', False)
ENABLE_GPU = config.get('enable_gpu', False)

# int/float constant
PRESS_AND_HOLD = config.get('press_&_hold')
TAP_AND_RELEASE = config.get('tap_&_release')
LOOPS = config.get('number_of_run', 50)
CONFIDENCE = config.get('confidence_threshold', 0.8)
PARALLEL_TRAINING = config.get('multi_parallel_training', ['LDPLayer'])
if len(PARALLEL_TRAINING) > 3:
    raise 'please check your parrallel training setting in your config, it should have a max of no more than 3 emulator names...'
WINNING = config.get('reward_rules')['reward_for_winning']
LOSING = config.get('reward_rules')['reward_for_losing']
DRAWING = config.get('reward_rules')['reward_for_draw']
DYING = config.get('reward_rules')['reward_for_dying']
SHOT_SUCCESS = config.get('reward_rules')['reward_for_successful_shooting']
DAMAGE_TAKEN = config.get('reward_rules')['reward_for_taking_damage']
WASTED_EQUIPMENT = config.get('reward_rules')['reward_for_wasting_equipment']
