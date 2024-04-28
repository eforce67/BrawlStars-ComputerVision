import yaml

with open('resources/config/settings.yaml', 'r') as configuration_file:
    config = yaml.safe_load(configuration_file)

# Boolean constants
SOURCE_TRAINING = config.get('load_training', False)
ENABLE_GPU = config.get('enable_gpu', False)

# Integer/float constants
SHOT_DELAY = config.get('shot_delay', 0.5)
RANGE_LIMIT = config.get('range_distance_limit', 500)
PRESS_AND_HOLD = config.get('press_&_hold')
TAP_AND_RELEASE = config.get('tap_&_release')
LOOPS = config.get('number_of_run', 50)
CONFIDENCE = config.get('confidence_threshold', 0.8)
PARALLEL_TRAINING = config.get('multi_parallel_training', ['LDPLayer'])
if len(PARALLEL_TRAINING) > 3:
    raise ValueError('Please check your parallel training setting in your config, it should have a maximum of no more than 3 emulator names...')

# Reward rules
REWARD_RULES = config.get('reward_rules')
WINNING = REWARD_RULES.get('reward_for_winning')
LOSING = REWARD_RULES.get('reward_for_losing')
DRAWING = REWARD_RULES.get('reward_for_draw')
DYING = REWARD_RULES.get('reward_for_dying')
SHOT_SUCCESS = REWARD_RULES.get('reward_for_successful_shooting')
DAMAGE_TAKEN = REWARD_RULES.get('reward_for_taking_damage')
WASTED_EQUIPMENT = REWARD_RULES.get('reward_for_wasting_equipment')
