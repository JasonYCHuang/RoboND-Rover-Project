import numpy as np

def throttle_base_on_limit(Rover):
    if Rover.vel < Rover.max_vel:
        return Rover.throttle_set
    else:
        return 0

def mode_pick_up(Rover):
    Rover.mode = 'stop'
    Rover.brake = Rover.brake_set
    Rover.steer = 0
    Rover.throttle = 0

def mode_near_sample(Rover):
    Rover.mode = 'stop'
    Rover.brake = Rover.brake_set
    Rover.steer = 0
    Rover.throttle = 0
    Rover.send_pickup = True
    Rover.samples_collected += 1

def mode_find_rock(Rover):
    Rover.mode = 'find_lock'
    Rover.brake = 0
    Rover.steer = np.clip(np.mean(Rover.rok_angles * 180/np.pi), -15, 15)
    Rover.throttle = throttle_base_on_limit(Rover)

def mode_continue_forward(Rover):
    Rover.brake = 0
    Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15, 15)
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
    Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15, 15)
    Rover.throttle = throttle_base_on_limit(Rover)

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
            mode_near_sample(Rover)
        elif len(Rover.rok_dists) > 0:
            mode_find_rock(Rover)
        # Check for Rover.mode status
        elif Rover.mode == 'forward': 
            # If mode is forward, navigable terrain looks good 
            # and velocity is below max, then throttle 
            if len(Rover.nav_angles) >= Rover.stop_forward:
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

    return Rover
