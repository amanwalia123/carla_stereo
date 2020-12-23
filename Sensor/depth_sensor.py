from utility import *

class DepthCamera(object):
  
    def __init__(self, parent_actor, _name = "camera",
                 pos_x=0.0, pos_y=0.0, pos_z=0.0,
                 rot_x=0.0, rot_y=0.0, rot_z=0.0,
                 focal_length=950.0, fov=90.0, gamma_correction=2.2,
                 image_size_x = 1920,image_size_y = 1280):

        self._parent = parent_actor
        self.name = _name

        self.world = self._parent.get_world()
        self.fov = fov
        self.focal_distance = focal_length
        self.gamma = gamma_correction
        self.image_size_x,self.image_size_y = image_size_x,image_size_y
        self.location = (pos_x,pos_y,pos_z)
        self.rotation = (rot_x, rot_y, rot_z)


    def construct_sensor(self):
        bp = self.world.get_blueprint_library().find('sensor.camera.depth')
        
        bp.set_attribute('fov', str(self.fov))
        bp.set_attribute('image_size_x', str(self.image_size_x))
        bp.set_attribute('image_size_y', str(self.image_size_y))

        cam_transform = carla.Transform(
                                        carla.Location(x = self.location[0], y = self.location[1], z = self.location[2]),
                                        carla.Rotation(pitch = self.rotation[1], yaw = -self.rotation[2], roll = self.rotation[0])
                                       )
        return self.world.spawn_actor(bp, cam_transform, attach_to=self._parent)
