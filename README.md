## Game of Code ##

* Clone the project
* Goto projet folder
* run python setup.py develop
* Create Your client file as goc/clients/<your_name>.py
* Create shoot function in <your_name>.py file

Example: test_client.py(path: goc/clients/test_client.py)

```python

import random
def shoot(current_position,all_targets,bullets):
	"""
	current_position: tuple=(x,y)
	targets={
		{"object_id":<object_id>,
		"position" : (x,y),
		"speed": (x,y)}
	}
	bullets: Total remaning bullet count	
	
	Important Notes:
	Grid Size		= 100 x 100
	Bullet Speed 	= (1,1)
	Shooter Speed 	= (1,0)
	Target Speed 	= (speed_x,speed_y): 
				speed_x or speed_y can be negative,0 or positive
	
	New Bullet will have position= ( shooter_x , shooter_y + 1)
	Bullets or targets will be destroyed if it goes out of grid in any axis
	Grid keeps generating targets any random position and with random speed
	"""
	x=current_position[0]
	y=current_position[1]
	for target in all_targets:
		target_x=target["position"][0]
		target_y=target["position"][1]
		speed_x=target["speed"][0]
		speed_y=target["speed"][1]		
		#TODO: Check shooter accuracy and		
		# Return True if bullet would hit target 
	return random.randint(0,5)==0
```
* To run project, python goc/run.py

* Objective: Program shooter when to shoot so that it would hit a moving target.

# Output Items #
* Blue: Bullet
* Red: Targets
* Brown: Shooter

# Initial Items#
* Total Bullets:50
* Total Iteration/Steps:300


