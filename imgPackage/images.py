from imgPackage import png

def load(filename):
    with open(filename, mode='rb') as f:
        reader = png.Reader(file=f)
        w, h, png_img, _ = reader.asRGB8()
        w *= 3
        return [ [ (line[i],line[i+1],line[i+2]) 
                   for i in range(0, w, 3) ]
                 for line in png_img ]
    
def save(img, filename):
    pngimg = png.from_array(img,'RGB')
    pngimg.save(filename)

