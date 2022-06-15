from imgPackage import png

'''
    It allows you to analyze and edit and save images 
    with png extension.
'''

def load(filename):
    
    '''
        Returns a matrix containing the RGB tuples 
        of the specified image.
    '''
    
    with open(filename, mode='rb') as f:
        reader = png.Reader(file=f)
        w, h, png_img, _ = reader.asRGB8()
        w *= 3
        return [ [ (line[i],line[i+1],line[i+2]) 
                   for i in range(0, w, 3) ]
                 for line in png_img ]
    
def save(img, filename):
    
    '''
        Saves the specified matrix (made up of tuples 
        containing RGB channels) in the specified path.
    '''
    
    pngimg = png.from_array(img,'RGB')
    pngimg.save(filename)

