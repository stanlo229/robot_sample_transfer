from numpy import load

data = load('map_param.npz')
lst = data.files
for item in lst:
    print(item)
    print(data[item])