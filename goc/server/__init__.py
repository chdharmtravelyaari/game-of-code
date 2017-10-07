from datetime import datetime 
import random
import sqlite3
import os
import json
import goc
def dict_factory(cursor, row):
	d = {}
	for idx, col in enumerate(cursor.description):
		d[col[0]] = row[idx]
	return d


PATH=os.path.join(os.path.dirname(goc.__file__),"data")
file_name=datetime.now().strftime("%Y-%m-%d %H-%M-%S") + ".db"
file_path=os.path.join(PATH,file_name)
conn = sqlite3.connect(file_path)
conn.row_factory = dict_factory

max_x=100
max_y=100
max_speed_x=1
max_speed_y=1
total_bullets=50

starting_targets=20
def setup():
	cursor = conn.cursor()
	cursor.execute("""
		CREATE TABLE MATRIX
		(
			step INTEGER,
			x INTEGER,
			y INTEGER,
			object_type TEXT,
			object_id INTEGER
		)
		""")

	cursor.execute("""
		CREATE TABLE OBJECTS
		(
			object_id INTEGER  PRIMARY KEY,
			name TEXT,
			object_type TEXT,		
			speed_x INTEGER,
			speed_y INTEGER,
			active INTEGER,
			shooter INTEGER		
		)
		""")
	cursor.execute("""
		CREATE TABLE bullets
		(
			bullet INTEGER
			,shooter INTEGER
			,hit INTEGER
		)
		""")
	conn.commit()

def create_object(name,object_type,start_position,speed=(0,0),current_step=0,active=1):
	cursor = conn.cursor()
	cursor.execute("""
	INSERT INTO OBJECTS
	(	
		name,
		object_type,
		speed_x,
		speed_y,
		active
	)
	VALUES(
		?,
		?,
		?,
		?,
		?
	);
	""", 
	(name,object_type,speed[0],speed[1],active))
	object_id=cursor.lastrowid
	cursor.execute("""
	INSERT INTO MATRIX
	(
		step,
		x,
		y,
		object_type,
		object_id
	)
	VALUES(
		?,
		?,
		?,
		?,
		?
	)
	""", (
		current_step
		,start_position[0]
		,start_position[1]
		,object_type,
		object_id
		)
	)	
	conn.commit()
	return object_id

def get_all_targets(current_step):
	cursor = conn.cursor()
	items=cursor.execute("""
		SELECT 
			o.speed_x
			,o.speed_y						
			,m.*
		FROM OBJECTS o
		INNER JOIN MATRIX m ON m.object_id=o.object_id
		WHERE m.step=? AND m.object_type='target' AND o.active=1
		""", (current_step,)).fetchall()
	targets=[]
	for item in items:
		targets.append({"object_id":item["object_id"],"position" : (item["x"],item["y"]),"speed": (item["speed_x"],item["speed_y"])})
	return targets

def move_all_objects(current_step,max_x,max_y,all_shooters):
	cursor = conn.cursor()
	items=cursor.execute("""
		SELECT 
			o.speed_x
			,o.speed_y						
			,m.*
		FROM OBJECTS o
		INNER JOIN MATRIX m ON m.object_id=o.object_id
		WHERE m.step=?  AND o.active=1
		""", (current_step,)).fetchall()
	#print items
	for item in items:
		object_id=item["object_id"]
		speed_x=item["speed_x"]
		speed_y=item["speed_y"]
		position=(item["x"],item["y"])
		new_position=(position[0]+speed_x, position[1]+speed_y)
		new_position=(new_position[0] % max_x, new_position[1] % max_y)
		object_type=item["object_type"]
		cursor.execute("""
			INSERT INTO MATRIX
			(
				step,
				x,
				y,
				object_type,
				object_id
			)
			VALUES(
				?,
				?,
				?,
				?,
				?
			)
			""", (
				current_step+1
				,new_position[0]
				,new_position[1]
				,object_type,
				object_id
				)			
			)
		#print object_id,object_type,new_position
		if object_id in all_shooters:			
			all_shooters[object_id]["position"]=new_position
	conn.commit()			

def detect_collision(current_step):
	cursor = conn.cursor()
	items=cursor.execute("""
		SELECT 
			m1.object_id bullet
			,m2.object_id target
			,m1.x
			,m1.y
		FROM MATRIX m1
		INNER JOIN MATRIX m2 ON 
			m1.object_type ='bullet'
			AND m2.object_type='target'
			AND m1.x = m2.x 
			AND m1.y = m2.y
		WHERE 
			m1.step=? 
			AND
			m2.step=?
		""", (current_step,current_step)).fetchall()	
	targets=[]
	bullets=[]
	for item in items:
		bullet=item["bullet"]
		cursor.execute("""
			UPDATE OBJECTS
				set active=0
			WHERE object_id=?
			""",(bullet,))
		cursor.execute("""
			UPDATE BULLETS
				set hit=1
			WHERE bullet=?
			""",(bullet,))
		
		target=item["target"]
		cursor.execute("""
			UPDATE OBJECTS
				set active=0
			WHERE object_id=?
			""",(target,))
		print "hit",current_step,bullet,target, "at=",item["x"],item["y"]
	conn.commit()

def detect_end(current_step,max_x,max_y):
	cursor = conn.cursor()
	items=cursor.execute("""
		SELECT 
			m.object_id bullet			
		FROM MATRIX m	

		WHERE
			(m.object_type ='bullet' OR m.object_type ='target')
			AND
			m.step=?
			AND 
			(m.x>=? OR m.y>=?)

		""", (current_step,max_x-1,max_y-1)).fetchall()	

	bullets=[]
	for item in items:
		bullet=item["bullet"]
		#bullets.append(str(bullet))
		cursor.execute("""
			UPDATE OBJECTS
				set active=0
			WHERE object_id =?
			""",(bullet,))	
		#print "end",bullet,current_step
	conn.commit()

def create_shooter(name,position):
	return create_object(name,"shooter",position,(1,0),0)

def create_bullet(shooter,current_step,shooter_position):
	position=(shooter_position[0],shooter_position[1]+1)
	bullet = create_object("","bullet",position,(1,1),current_step)	
	cursor=conn.cursor()
	cursor.execute("""
		INSERT INTO bullets
		(
			bullet
			,shooter
			,hit
		)
		VALUES
		(
			?
			,?
			,0
		)
		""",(bullet,shooter))
	return bullet

def create_target(current_step,max_x,max_y,max_speed_x,max_speed_y):
	x=random.randint(0,max_x-1)
	y=random.randint(0,max_y-1)
	speed_x=random.randint(-max_speed_x,max_speed_x)
	speed_y=random.randint(-max_speed_y,max_speed_y)
	return create_object("","target",(x,y),(speed_x,speed_y),current_step)

def run_step(current_step,all_shooters):	
	all_targets=get_all_targets(current_step)
	for object_id,client_details in all_shooters.iteritems():
		client=client_details["client"]
		current_position=client_details["position"]
		bullets=client_details["bullets"]
		signal=False
		if bullets:
			signal = client.shoot(current_position,all_targets,bullets)
		print "bullets=",bullets,"; shoot=",signal
		if signal and bullets:
			create_bullet(object_id,current_step,current_position)
			client_details["bullets"]-=1
	detect_collision(current_step)
	detect_end(current_step,max_x,max_y)
	move_all_objects(current_step,max_x,max_y,all_shooters)
	

def run(total_steps):	
	from goc import clients
	from goc.clients import test_client
	import pkgutil
	from importlib import import_module	

	client_list=[]

	for mod_client in  pkgutil.walk_packages(clients.__path__):
		path=".".join(["goc.clients",mod_client[1]])		
		mod = import_module(path)
		if hasattr(mod,"shoot")	:
			client_list.append(mod)	
	
	all_positions_x=list(range(max_y))
	all_shooters={}
	for client in client_list :
		name =client.__name__
		position_x=random.sample(all_positions_x,1)[0]
		current_position=(position_x,0)
		#print name,current_position
		object_id=create_shooter(name,current_position)
		all_positions_x.remove(position_x)
		all_shooters[object_id]={"client":client,"position":current_position,"bullets":total_bullets}

	current_step=0
	for i in range(starting_targets):
		create_target(current_step,max_x,max_y,max_speed_x,max_speed_y)
	#print get_all_targets(0)
	for current_step in range(total_steps):
		run_step(current_step,all_shooters)
		if random.randint(0,3)==0:
			create_target(current_step+1,max_x,max_y,max_speed_x,max_speed_y)
		#get_all_targets(i)
def caculate_result():
	cursor=conn.cursor()
	items = cursor.execute("""
		SELECT o.object_id,o.name,b.hit,COUNT(*) total FROM BULLETS b
		INNER  JOIN OBJECTS o ON o.object_id=b.shooter
		WHERE o.object_type='shooter'
		GROUP BY o.object_id,o.name,b.hit
		""").fetchall()
	result={}
	for item in items:
		object_id=item["object_id"]
		stats=result.get(object_id,{"name":item["name"]})
		stats[str(item["hit"])]=item["total"]
		result[object_id]=stats

	for object_id,stats in result.iteritems():
		stats["total"]=stats.get("0",0)+stats.get("1",0)
		stats["hits"]=stats.get("1",0)
	return result

def generate_output(steps):
	import output
	cursor=conn.cursor()
	all_shooters = cursor.execute("""
		SELECT object_id,name,object_type FROM OBJECTS WHERE object_type='shooter'
		""").fetchall()

	itr = cursor.execute("""
		SELECT  
			step
			,x
			,y
			,object_type
			,object_id
		FROM MATRIX
		ORDER BY step

		""").fetchall()
	matrix=[None]*(steps+1)
	for item in itr:
		step =item["step"]
		x=item["x"]
		y=item["y"]
		object_type=item["object_type"]
		o={"x":x,"y":y,"o":object_type[0]}
		if not matrix[step]:
			matrix[step]=[]
		matrix[step].append(o)
	
	result = caculate_result()
	data={"shooters":all_shooters,"matrix":matrix,"result":result}
	output.write_output(PATH,data,max_x,max_y)


def main():
	setup()

	#create_object("","shooter",(5,0),(1,0))
	#create_shooter("",(5,0))
	#create_object("kapala","target",(10,10),(-1,0))
	#create_object("bullet1","bullet",(5,1),(1,1))
	total_steps=300
	run(total_steps)
	generate_output(total_steps)
	

if __name__ == '__main__':
	main()