
connections = []
connections.append({"src":1, "dst":2})
connections.append({"src":2, "dst":3})
connections.append({"src":1, "dst":3})
connections.append({"src":3, "dst":2})

def find(src=None, dst=None):
    conns = []
    
    if src is None and dst is None:
        return []

    for conn in connections:
        if src:
            if src != conn["src"]:
                continue
        if dst:
            if dst != conn["dst"]:
                continue


        conns.append(conn)
    return conns

print find()
