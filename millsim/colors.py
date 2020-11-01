BV_RANGES_RED   = [(-.4, 0),       (0, .4),       (.4, 2.1)]
BV_POLIES_RED   = [(.61, .11, .1), (.83, .17, 0), (1, 0, 0)]

BV_RANGES_GREEN = [(-.4, 0),       (0, .4),       (.4, 1.6),      (1.6, 2)]
BV_POLIES_GREEN = [(.7, .07, .1),  (.87, .11, 0), (.98, -.16, 0), (.82, 0, -.5)]

BV_RANGES_BLUE  = [(-.4, .4),   (.4, 1.5),     (1.5, 1.94)]
BV_POLIES_BLUE  = [(1, .0, .0), (1, -.47, .1), (.63, 0, -.6)]

def piecewise_interp(x, ranges, polies, dfl):
    for i, rang in enumerate(ranges):
        if rang[0] <= x < rang[1]:
            p = polies[i]
            t = (x - rang[0]) / (rang[1] - rang[0])
            return p[0] + p[1] * t + p[2] * t * t

    return dfl

def bv2rgb(bv):
    if bv < -.4:
        bv = .4
    
    if bv > 2:
        bv = 2
    
    return (piecewise_interp(bv, BV_RANGES_RED,   BV_POLIES_RED, 0),   \
            piecewise_interp(bv, BV_RANGES_GREEN, BV_POLIES_GREEN, 0), \
            piecewise_interp(bv, BV_RANGES_BLUE,  BV_POLIES_BLUE, 0))
    