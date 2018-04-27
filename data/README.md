Format of data files
====

Each data JSON file will follow the following format (which the Python code will generate and visualize code will read):

    {
        "meta": { // "meta": basic imformation for rendering
            "radius": 0.005, // "radius": radius of rod for rendering
            "closed": false // "closed": whether it is a staight beam (false) or a circular shape (true)
        },
        "frames": [ // "frames": an array of frames, must be in correct order
            {
                "time": 0, // "time": time of current frame,
                "data:" [0, 0, 1, 0, 2, 0, 3, 0.1] // "data": original q array, locations of nodes (x0, y0, x1, y1, x2, y2, etc.)
            }
        ]
    }