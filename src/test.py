import os

a = 'D:/Administrator/Downloads/NewCG'
print(os.listdir(a))
for i in os.listdir(a):
    path = os.path.join(a, i)
    if os.path.isdir(path):
        print(f'{i} is folder')
{
    'folder 1': {
        'folder': [
            {},
        ],
        'file': [
            '',
        ]
    }
}
