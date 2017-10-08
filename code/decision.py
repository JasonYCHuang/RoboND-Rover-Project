import numpy as np

def throttle_base_on_limit(Rover):
    if Rover.vel < Rover.max_vel:
        return Rover.throttle_set
    else:
        return 0

def steer_base_on_scene(angles):
    steer = 0
    if len(angles) > 0:
        steer = np.clip(np.mean(angles * 180/np.pi), -15, 15)
    if abs(steer) < 5:
        steer = 0
    return steer

# - - - - - Mode find_rock - - - - -
def mode_approach_rock(Rover):
    Rover.mode = 'find_rock'
    Rover.brake = 0
    Rover.steer = steer_base_on_scene(Rover.rok_angles)
    Rover.throttle = throttle_base_on_limit(Rover)

def mode_pick_up(Rover):
    Rover.mode = 'stop'
    Rover.brake = Rover.brake_set
    Rover.steer = 0
    Rover.throttle = 0

def mode_near_rock(Rover):
    Rover.mode = 'stop'
    Rover.brake = Rover.brake_set
    Rover.steer = 0
    Rover.throttle = 0
    Rover.send_pickup = True
    Rover.samples_collected += 1

# - - - - - Mode forward - - - - -
def mode_continue_forward(Rover):
    Rover.brake = 0
    Rover.steer = steer_base_on_scene(Rover.nav_angles)
    Rover.throttle = throttle_base_on_limit(Rover)

def mode_terminate_forward(Rover):
    Rover.mode = 'stop'
    Rover.brake = Rover.brake_set
    Rover.steer = 0
    Rover.throttle = 0

def mode_keep_going(Rover):
    Rover.brake = 0
    Rover.steer = 0
    Rover.throttle = throttle_base_on_limit(Rover)

# - - - - - Mode stop - - - - -
def mode_force_stop(Rover):
    Rover.brake = Rover.brake_set
    Rover.steer = 0
    Rover.throttle = 0

def mode_turn_around(Rover):
    Rover.brake = 0
    Rover.steer = -15
    Rover.throttle = 0

def mode_go_forward(Rover):
    Rover.mode = 'forward'
    Rover.brake = 0
    Rover.steer = steer_base_on_scene(Rover.nav_angles)
    Rover.throttle = throttle_base_on_limit(Rover)

# - - - - - Mode stuck - - - - -
def mode_resolve_stuck(Rover):
    Rover.mode = 'forward'
    Rover.brake = 0
    Rover.steer = 0
    Rover.throttle = throttle_base_on_limit(Rover)
    reset_stuck_counter(Rover)

def mode_encounter_stuck(Rover):
    Rover.mode = 'stuck'
    Rover.brake = 0
    Rover.steer = -15
    Rover.throttle = 0
    Rover.stuck_yaw = Rover.yaw

def mode_in_stuck(Rover):
    if Rover.throttle > 0:
        Rover.brake = Rover.brake_set
        Rover.steer = -15
        Rover.throttle = 0
    else:
        Rover.brake = 0
        Rover.steer = -15
        Rover.throttle = 0

# - - - - - Helper stuck - - - - -
def reset_stuck_counter(Rover):
    Rover.stuck_counter = 0

def increase_stuck_counter(Rover):
    Rover.stuck_counter += 1

def update_stuck_status(Rover):
    if Rover.mode == 'forward' and Rover.vel < Rover.stuck_vel:
        increase_stuck_counter(Rover)
    elif Rover.mode == 'find_rock' and Rover.vel < Rover.stuck_vel:
        increase_stuck_counter(Rover)
    else:
        reset_stuck_counter(Rover)

# This is where you can build a decision tree for determining throttle, brake and steer 
# commands based on the output of the perception_step() function
def decision_step(Rover):
    
    # Implement conditionals to decide what to do given perception data
    # Here you're all set up with some basic functionality but you'll need to
    # improve on this decision tree to do a good job of navigating autonomously!

    # Example:
    # Check if we have vision data to make decisions with
    if Rover.nav_angles is not None:
        # Check for Rover.mode status
        if Rover.picking_up == 1:
            mode_pick_up(Rover)
        elif Rover.near_sample == 1:
            mode_near_rock(Rover)
        elif len(Rover.rok_dists) > 0:
            mode_approach_rock(Rover)

        # Check for Rover.mode status
        elif Rover.mode == 'stuck':
            if abs(Rover.yaw - Rover.stuck_yaw) >= 60:
                mode_resolve_stuck(Rover)
            else:
                mode_in_stuck(Rover)

        elif Rover.mode == 'forward':
            # If mode is forward, navigable terrain looks good 
            # and velocity is below max, then throttle
            if Rover.stuck_counter > Rover.stuck_limit:
                mode_encounter_stuck(Rover)
            elif len(Rover.nav_angles) >= Rover.stop_forward:
                mode_continue_forward(Rover) 
            # If there's a lack of navigable terrain pixels then go to 'stop' mode
            elif len(Rover.nav_angles) < Rover.stop_forward:
                mode_terminate_forward(Rover)

        # If we're already in "stop" mode then make different decisions
        elif Rover.mode == 'stop':
            # If we're in stop mode but still moving keep braking
            if Rover.vel > 0.2:
                mode_force_stop(Rover)
            # If we're not moving (vel < 0.2) then do something else
            elif Rover.vel <= 0.2:
                # Now we're stopped and we have vision data to see if there's a path forward
                if len(Rover.nav_angles) < Rover.go_forward:
                    mode_turn_around(Rover)
                if len(Rover.nav_angles) >= Rover.go_forward:
                    mode_go_forward(Rover)

    # Just to make the rover do something 
    # even if no modifications have been made to the code
    else:
        mode_keep_going(Rover)

    # check whether it is stuck
    update_stuck_status(Rover)

    return Rover
