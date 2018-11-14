# BlenderCarRigAutomization
This repository allows to automatically attach a car rig (https://gumroad.com/l/carrigultimate) to vehicle models and motion curves

The default vehicle model contained in this repository is a small modification of the one provided
[here](https://www.blendswap.com/blends/view/44360).

Clone the repository with the following command to ensure that the submodules are correctly initialized
```
git clone --recurse-submodules https://github.com/SBCV/BlenderCarRigAutomization.git
```

Run 
```
python Execute_Attach_Rig_to_Car_Model.py
```
to automatically create the following config files:
```
BlenderCarRigAutomization/BlenderUtility/Configs/blender_script_executor.cfg
BlenderCarRigAutomization/configs/attach_rig_to_car_model.cfg
```
Adjust the path to the blender executable in ```blender_script_executor.cfg```

and the path to the car rig blend file in ```attach_rig_to_car_model.cfg```

Run (again)
```
python Execute_Attach_Rig_to_Car_Model.py
```
to attach the vehicle rig to a specific car model. 
The Blender file with the rigged vehicle is automatically opened afterwards - close it. 

Run 
```
python Execute_Attach_Car_Rig_To_Curve.py
```
to attach the rigged vehicle model to a given motion trajectory.
This automatically opens a Blender file with the rigged vehicle attached to a trajectory in a simple environment. 

## License
Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)

https://creativecommons.org/licenses/by-nc-sa/4.0/deed.en
