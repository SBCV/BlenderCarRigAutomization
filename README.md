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
to automatically create the following config file:
```
BlenderCarRigAutomization/BlenderUtility/Configs/blender_script_executor.cfg
```
Adjust the path to the blender executable in ```blender_script_executor.cfg```.

Run (again)
```
python Execute_Attach_Rig_to_Car_Model.py
```
to attach the vehicle rig to a specific car model.

Run 
```
python Execute_Attach_Rig_to_Car_Model.py
```
to attach the rigged vehicle model to a given motion trajectory.


