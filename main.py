#!/usr/bin/env python

# Copyright (c) 2019 Computer Vision Center (CVC) at the Universitat Autonoma de
# Barcelona (UAB).
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.

from utility import *

# parser = argparse.ArgumentParser(description="Generate dataset using CARLA")

# parser.add_argument('--town',default="Town01",
#                     choices=["Town01","Town02","Town03","Town04","Town05"],
#                     help="town map to run")

# savedir = ""

TOWN = "Town01"
NIGHT_MODE = False

IMAGE_WIDTH=1920
IMAGE_HEIGHT=1280

GATED_WIDTH=1280
GATED_HEIGHT=720

BASELINE = 1.2

MAX_FRAMES = 1500

daytime = "day" if not NIGHT_MODE else "night"
RESULT_DIR = "/mnt/HDD/CARLA_dataset/{}_{}".format(daytime,TOWN)


cam0_dir = "%s/%s"%(RESULT_DIR,"cam_left")
os.makedirs(cam0_dir,exist_ok=True)

cam1_dir = "%s/%s"%(RESULT_DIR,"cam_right")
os.makedirs(cam1_dir,exist_ok=True)

cam_gated_dir = "%s/%s"%(RESULT_DIR,"cam_gated")
os.makedirs(cam_gated_dir,exist_ok=True)

depth0_dir = "%s/%s"%(RESULT_DIR,"depth_left")
os.makedirs(depth0_dir,exist_ok=True)

depth1_dir = "%s/%s"%(RESULT_DIR,"depth_right")
os.makedirs(depth1_dir,exist_ok=True)

depth_gated_dir = "%s/%s"%(RESULT_DIR,"depth_gated")
os.makedirs(depth_gated_dir,exist_ok=True)

def main():
    actor_list = []
    total_frames = 0
    pygame.init()

    # display = pygame.display.set_mode((IMAGE_WIDTH, IMAGE_HEIGHT),pygame.HWSURFACE | pygame.DOUBLEBUF)
    font = get_font()
    clock = pygame.time.Clock()

    client = carla.Client('localhost', 2000)
    
    client.set_timeout(2.0)

    # world = client.get_world()
    world =  client.load_world(TOWN)
    weather = world.get_weather()
    weather.sun_altitude_angle = -90.0 if NIGHT_MODE else 90.0
    world.set_weather(weather) 

    try:
        map = world.get_map()

        start_pose = random.choice(map.get_spawn_points())
        waypoint = map.get_waypoint(start_pose.location)

        blueprint_library = world.get_blueprint_library()

        default_car = blueprint_library.find("vehicle.tesla.model3")

        vehicle = world.spawn_actor(default_car, start_pose)

        actor_list.append(vehicle)
        vehicle.set_simulate_physics(False)

        rgb_cam0 = RGBCamera(vehicle,"Left Camera",pos_x=1.2,pos_y=-BASELINE/2,pos_z=1.5,rot_x=0,rot_y=0,rot_z=0,image_size_x=IMAGE_WIDTH,image_size_y=IMAGE_HEIGHT).construct_sensor()
        actor_list.append(rgb_cam0)
        
        rgb_cam1 = RGBCamera(vehicle,"Right Camera",pos_x=1.2,pos_y=BASELINE/2,pos_z=1.5,rot_x=0,rot_y=0,rot_z=0,image_size_x=IMAGE_WIDTH,image_size_y=IMAGE_HEIGHT).construct_sensor()
        actor_list.append(rgb_cam1)

        gated_cam = RGBCamera(vehicle,"Gated Camera",pos_x=1.2,pos_y=0.0,pos_z=1.5,rot_x=0,rot_y=0,rot_z=0,image_size_x=GATED_WIDTH,image_size_y=GATED_HEIGHT).construct_sensor()
        actor_list.append(gated_cam)

        depth_cam0 = DepthCamera(vehicle,"(Depth)Left Camera",pos_x=1.2,pos_y=-BASELINE/2,pos_z=1.5,rot_x=0,rot_y=0,rot_z=0,image_size_x=IMAGE_WIDTH,image_size_y=IMAGE_HEIGHT).construct_sensor()
        actor_list.append(depth_cam0)
        
        depth_cam1 = DepthCamera(vehicle,"(Depth)Right Camera",pos_x=-0.2,pos_y=BASELINE/2,pos_z=1.5,rot_x=0,rot_y=0,rot_z=0,image_size_x=IMAGE_WIDTH,image_size_y=IMAGE_HEIGHT).construct_sensor()
        actor_list.append(depth_cam1)

        depth_gated = DepthCamera(vehicle,"(Depth)Gated Camera",pos_x=-0.2,pos_y=0.0,pos_z=1.5,rot_x=0,rot_y=0,rot_z=0,image_size_x=GATED_WIDTH,image_size_y=GATED_HEIGHT).construct_sensor()
        actor_list.append(depth_gated)

        # Create a synchronous mode context.
        with CarlaSyncMode(world, rgb_cam0, rgb_cam1, gated_cam, depth_cam0, depth_cam1,depth_gated, fps=30) as sync_mode:
            while total_frames < MAX_FRAMES:
                # if should_quit():
                #     return
                clock.tick()

                # Advance the simulation and wait for the data.
                snapshot, image_left, image_right, image_gated, depth_left, depth_right, depth_gated = sync_mode.tick(timeout=5.0)

                # Choose the next waypoint and update the car location.
                waypoint = random.choice(waypoint.next(1.5))
                vehicle.set_transform(waypoint.transform)

                depth_left.convert(carla.ColorConverter.Depth)
                
                fps = round(1.0 / snapshot.timestamp.delta_seconds)

                # Draw the display.
                # draw_image(display, depth_left)

                # depth_left.convert(carla.ColorConverter.Depth)

                save_image(image_left,cam0_dir)
                save_image(image_right,cam1_dir)
                save_image(image_gated,cam_gated_dir)
                
                save_depth(depth_left,depth0_dir)
                save_depth(depth_right,depth1_dir)
                save_depth(depth_gated,depth_gated_dir)
                
                # save_depth(depth_left,"./")

                # draw_image(display, image_semseg, blend=True)
                # display.blit(
                #     font.render('% 5d FPS (real)' % clock.get_fps(), True, (255, 255, 255)), (8, 10))
                # display.blit(
                #     font.render('% 5d FPS (simulated)' % fps, True, (255, 255, 255)), (8, 28))
                
                # print('% 5d FPS (real)' % clock.get_fps(),end="\r")
                # print('% 5d FPS (simulated)' % fps,end="\r")
                # pygame.display.flip()

                total_frames += 1
                print("Frames saved = %d "%total_frames,end="\r")

    finally:

        print('destroying actors.')
        for actor in actor_list:
            actor.destroy()

        # pygame.quit()
        print('done.')


if __name__ == '__main__':

    try:

        main()

    except KeyboardInterrupt:
        print('\nCancelled by user. Bye!')
