Format of data files
====

Each data JSON file will follow the following format (which the Python code will generate and visualize code will read):

    {
        "meta": { // "meta": [REQUIRED] basic imformation for rendering
            "radius": 0.005, // "radius": [REQUIRED] radius of rod for rendering
            "closed": false, // "closed": [REQUIRED] whether it is a staight beam (false) or a circular shape (true),
            "ground": false, // "ground": [OPTIONAL] if set to true, will draw a ground at y = 0
            "groundAngle": -15 // "groundAngle": [OPTIONAL] angle of ground, in degrees, CCW
            "numberOfStructure": 2 // "numberOfStructure": [OPTIONAL] number of structures, if more than one
        },
        "frames": [ // "frames": [REQUIRED] an array of frames, must be in correct order
            {
                "time": 0, // "time": [REQUIRED] time of current frame,
                "data:" [0, 0, 1, 0, 2, 0, 3, 0.1] // [REQUIRED] "data": original q array, locations of nodes (x0, y0, x1, y1, x2, y2, etc.); if numberOfStructure is specified, this should be an array of arrays instead (even if numberOfStructure = 1)
            },
            ...
        ],
        "code": "def runDER(): ..." // [OPTIONAL] "code": backup of the code used for getting this result (in case you forget some parameters) 
    }