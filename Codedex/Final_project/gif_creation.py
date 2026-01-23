import imageio.v3 as iio

filenames = ['Python/Codedex/Final_project/Images/team-pic1.png', 
             'Python/Codedex/Final_project/Images/team-pic2.png']
images = [ ]

for filename in filenames:
    images.append(iio.imread(filename))

iio.imwrite('Python/Codedex/Final_project/Images/team-pic.gif', images, duration=500, loop=0)