import json
import os
template = """

<!DOCTYPE html>
<html>
<head>
	<title>Game of Code | Bend the bullet</title>
	<style type="text/css">
		div.cell{
			width:7px;
			height:7px;
			border:1px solid lightgray;
			border-width: 1px 0 0 1px;
		}
		#grid{
			width:800px;			
		}
		#grid div.cell{
			float:left;
		}
		#grid div.cell.b{
			background-color:blue;
		}
		#grid div.cell.t{
			background-color: red;
		}
		#grid div.cell.s{
			border-color: black;
		}		
	</style>
	
</head>
<body>	
	<div id="grid" >
		#GRID#
	</div>		
	<div>
		<span id="step"></span>
	</div>
	<div id="step_counter" style="display:none">
	  <input type="range" min="1" max="100" value="50" class="slider" id="myRange">
	</div>
	<div id="result" style="padding:50px;display:none";>
		<h1>Result</h1>
		#result#
	</div>
	<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.2.1/jquery.js"></script>
	<script type="text/javascript">
		var data=#DATA#;
	</script>
	<script type="text/javascript">
		var grid=$("#grid").children();

		var grid_width_cells = 100;
		var grid_height_cells=100;
		function show_step(step_objects){
			$("#grid div.cell").removeClass("s");
			$("#grid div.cell").removeClass("t");
			$("#grid div.cell").removeClass("b");

			for (var i = step_objects.length - 1; i >= 0; i--) {
				var step_object=step_objects[i];
				var x=step_object.x;
				var y=step_object.y;
				var position=grid_width_cells*(99-y)+x;								
				$(grid[position]).addClass(step_object.o)
			}
		}
		var counter=0
		function next_step(){
			var step_objects=data.matrix[counter];

			if(step_objects){
				$("#step").text(counter);
				show_step(step_objects);
				counter++;	
			}else{
				show_result();
			}			
		}
		function show_result(){
			$("#result").show();
		}
		$("#step_counter").attr("min",0);
		$("#step_counter").attr("max",data.matrix.length);
		$("#step_counter").change(function(){
			counter=$("#step_counter").val();			
		});
		setInterval(next_step,400);
	</script>
</body>
</html>

"""
colors=["#6a860f","#906660","#a474f6","#3fb786","#1f1409","#a2a3a3","#996b77","#35ea28","#cecf66","#7422a1"]
def write_output(output_path,data,max_x,max_y):
	n=(max_x*(max_y+10))
	
	divs=['<div class="cell"></div>' for i in range(n)]
	str_divs="\n".join(divs)
	output = template.replace("#GRID#",str_divs)
	#shooters=data["shooters"]
	#shooters_div=[]
	#color_classes=[]
	#for i in range(len(shooters)):		
	#	shooters_div.append('<div style="background-color:'+colors[i]+'">'+shooters[i]["name"]+'</div>')		
	#
	#output = output.replace("#color_classes#",json.dumps(color_classes))
	output = output.replace("#DATA#",json.dumps(data))

	#output=output.replace("#shooters#","\n".join(shooters_div))

	result=data["result"]
	result_divs=[]
	for object_id,stats in result.iteritems():
		result_divs.append('<div style="padding:10px">')
		result_divs.append('<span>Name: '+stats["name"]+'</span>')
		result_divs.append('<span>ID: '+str(object_id)+'</span>')
		result_divs.append('<span>Attempt: '+str(stats["total"])+'</span>')
		result_divs.append('<span>Hits: '+str(stats["hits"])+'</span>')
		result_divs.append('</div>')
	output = output.replace("#result#","\n".join(result_divs))
	file_path=os.path.join(output_path,"output.html")
	with open(file_path,"wb") as f:
		f.write(output)
		
	print "Result at", file_path
