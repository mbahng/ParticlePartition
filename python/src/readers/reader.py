from src.coverers.data_structs import Environment, Point
import time
from src.debug import * 


def readFile(filepath, stop:int = 128, performance:bool=False): 
    # returns a list of wedges 
    # Each wedge is represented by tuple (env, pnts) 
    # env is an Environment, and pnts is a list of Points 
    
    start = time.time()
    
    # Create a list of events, with each event consisting of an environment and its list of Points 
    events = [] 
    with open(filepath) as f: 
        line_index = 0
        for line in f: 
            if line.strip():
                
                tuples = line.strip()[1:-1].split("),(")
                tuples = [tup.split(",") for tup in tuples]
                
                list_of_Points = [Point(int(tupl[0]), float(tupl[1]), float(tupl[2]), float(tupl[3])) for tupl in tuples]
                radii = sorted(list(set([point.radius for point in list_of_Points])))
                num_layers = len(radii)
                
                env = Environment(top_layer_lim= 100.0, 
                                  beam_axis_lim = 15.0, 
                                  num_layers=num_layers, 
                                  radii=radii
                                )
                events.append((env, list_of_Points))
                
            line_index += 1 
            if line_index == stop: 
                break 
    
    if performance == True:
        print(f"Time Taken to Read File : {time.time() - start}s")
        
    return events 

def readUnaryFile(filepath, index_file, ix, performance:bool=False): 
    # env is an Environment, and pnts is a list of Points 
    
    start = time.time()
    fpos = -1
    with open(index_file, "rb") as f:
        f.seek(4 * ix)
        fpos = int.from_bytes(f.read(4), "big")
    
    # Create a list of events, with each event consisting of an environment and its list of Points 
    events = [] 
    with open(filepath) as f: 
        f.seek(fpos)
        line = f.readline().strip()
        tuples = line.strip()[1:-1].split("),(")
        tuples = [tup.split(",") for tup in tuples]
        
        list_of_Points = [Point(int(tupl[0]), float(tupl[1]), float(tupl[2]), float(tupl[3])) for tupl in tuples]
        radii = sorted(list(set([point.radius for point in list_of_Points])))
        num_layers = len(radii)
        
        env = Environment(top_layer_lim= 100.0, 
                            beam_axis_lim = 15.0, 
                            num_layers=num_layers, 
                            radii=radii
                        )
        events.append((env, list_of_Points))
                
    if performance == True:
        print(f"Time Taken to Read File : {time.time() - start}s")
        
    return events 


