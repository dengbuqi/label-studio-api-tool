'''
Updata Yolov5 data to label-studio 
'''
from label_studio_sdk import Client
import glob
from tqdm import tqdm

LABEL_STUDIO_URL = 'http://localhost:8080'
API_KEY = ''
YOLOV5_DATA_PATH = ''

# convert yolov5 data to LS percent units 
def convert_to_ls(x, y, width, height):
    return (x - (width/2)) * 100.0, (y - (height/2))  * 100.0, \
           width * 100.0, height * 100

# read yolov5 labels 
def read_labels(file_path):
    labels = []
    with open(file_path, 'r') as f:
        for line in f:
            label = line.split(' ')
            if len(line) == 0:
                continue
            labels.append(label)
    return labels

# read classes
cls = []
with open(f'{YOLOV5_DATA_PATH}/classes.txt') as file_in:
    for line in file_in:
        cls.append(line.replace('\n', ''))

ls = Client(url=LABEL_STUDIO_URL, api_key=API_KEY)
print('label-studio connnction status', ls.check_connection()['status'])

# create new projects
# labels = ''
# for c in cls:
#     labels += f'<Label value="{c}"/>\n'
# label_config = f'<View>\n<Image name="image" value="$image"/>\n<RectangleLabels name="label" toName="image">\n{labels}</RectangleLabels>\n</View>'
# print(label_config)
# project = ls.start_project(
#     title='Nave_Image_K',
#     label_config=label_config
# )

# get all projects
# projects = ls.get_projects()
# for project in projects:
#     print(project.get_params()['id'])

# get project by id
project = ls.get_project(id=24)
print(project.get_params()['id'])

image_paths = sorted(glob.glob(f'{YOLOV5_DATA_PATH}/images/*'))
label_paths = sorted(glob.glob(f'{YOLOV5_DATA_PATH}/labels/*'))

tbar = tqdm(zip(image_paths,label_paths))
for img_path, label_path in tbar:
    tbar.set_description(f'GEN {img_path.split("/")[-1].split(".")[0]}')
    labels = read_labels(label_path)
    ls_labels = []
    for label in labels:
        x,y,w,h = convert_to_ls(float(label[1]),float(label[2]),float(label[3]),float(label[4]))
        ls_labels.append((int(label[0]), x,y,w,h))

    # up_data
    project_id = project.import_tasks(img_path)
    results = []
    for ls_l in ls_labels:
        results.append(
            {
              "from_name": "label",
              "to_name": "image",
              "type": "rectanglelabels",
              "value": {
                "rotation": 0,
                "x": ls_l[1],
                "y": ls_l[2],
                "width": ls_l[3],
                "height": ls_l[4],
                "rectanglelabels": [
                  cls[ls_l[0]]
                ]
              }
            }
        )
    predictions = [
        {
          "model_version": "updata",
          "result": results,
          "task": project_id[0]
        }
      ]
    project.create_predictions(predictions)


project.create_annotations_from_predictions(model_versions='updata')