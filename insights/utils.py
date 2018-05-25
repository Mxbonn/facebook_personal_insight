import colorsys

def get_colors(N=5):
    return  [colorsys.hsv_to_rgb(x*1.0/N, 0.5, 0.5) for x in range(N)]

def m2hm(x, i):
    h = int(x/60)
    m = int(x%60)
    return '%(h)02d:%(m)02d' % {'h':h,'m':m}