import os
import sys
sys.path.append(os.getcwd())
import shutil
from label_studio_ml.model import LabelStudioMLBase
from label_studio_ml.utils import get_image_local_path, get_single_tag_keys, get_choice, is_skipped
import torch
from PIL import Image
from pathlib import Path
from yolov5 import train as yolov5train
from datetime import datetime
import yaml
import time

# convert to LS percent units 
def convert_to_ls(xmin, ymin, xmax, ymax, img_w, img_h):

    return (xmin/img_w) * 100.0, (ymin/img_h)  * 100.0, \
           (xmax-xmin)/img_w * 100.0, (ymax-ymin)/img_h * 100

def convert_to_yolo(xmin, ymin, w, h):
    return (xmin+(w/2))/100, (ymin+(h/2))/100, w/100, h/100

def get_bbox(completion, cls2number):
    bbox = []
    for v in completion['annotations'][0]['result']:
        xc,yc,w,h = convert_to_yolo(v['value']['x'], v['value']['y'], v['value']['width'], v['value']['height'])
        bbox.append((cls2number[v['value']['rectanglelabels'][0]], xc, yc, w, h))
    return bbox

class MyModel(LabelStudioMLBase):
    def __init__(self, batch_size=16, epochs=3, **kwargs):
        # don't forget to initialize base class...
        super(MyModel, self).__init__(**kwargs)
        self.model = torch.hub.load('./yolov5/', 'custom', path='./best.pt', source='local')
        self.model.eval()
        self.from_name, self.schema = list(self.parsed_label_config.items())[0]
        self.to_name = self.schema['to_name'][0]
        self.labels = self.schema['labels']
        self.batch_size = batch_size
        self.epochs = epochs
        self.cls2number = dict()
        for index,value in enumerate(self.labels):
            self.cls2number[value] = index

    def predict(self, tasks, **kwargs):
        predictions = []
        # Get annotation tag first, and extract from_name/to_name keys from the labeling config to make predictions
        for task in tasks:
            # for each task, return classification results in the form of "choices" pre-annotations
            image_path = get_image_local_path(task['data']['image'])
            im = Image.open(image_path)
            width, height = im.size
            start = time.time()
            results = self.model(im)
            print('#'*50)
            print('Time', time.time()-start)
            print('#'*50)
            results = results.pandas().xyxy[0]
            ls_results = []
            for index, row in results.iterrows():
                x,y,w,h = convert_to_ls(row['xmin'], row['ymin'], row['xmax'], row['ymax'], width, height)
                ls_results.append(
                    {
                        "from_name": self.from_name,
                        "to_name": self.to_name,
                        "type": "rectanglelabels",
                        "value": {
                            "rotation": 0,
                            "x": x,
                            "y": y,
                            "width": w,
                            "height": h,
                            "rectanglelabels": [
                                self.labels[row['class']]
                            ],
                            "confidence":row['confidence']
                        }
                        }
                )
            predictions.append({
                            "model_version": "updata",
                            "result": ls_results,
                            "score": results["confidence"].mean()
                        })
        return predictions

    # def fit(self, completions, workdir='.', **kwargs): 

    #     label_folder = '/home/deng/data/video_info_extraction/label-studio-api-tool/labels'
    #     image_folder = '/home/deng/data/video_info_extraction/label-studio-api-tool/images'
    #     if not os.path.exists(label_folder):
    #         os.makedirs(label_folder)
    #     else:
    #         shutil.rmtree(label_folder)
    #         os.makedirs(label_folder)
    #     if not os.path.exists(image_folder):
    #         os.makedirs(image_folder)
    #     else:
    #         shutil.rmtree(image_folder)
    #         os.makedirs(image_folder)

    #     for completion in completions:
    #         if is_skipped(completion):
    #             continue
    #         image_path = get_image_local_path(completion['data']['image'])
    #         shutil.copyfile(image_path, image_folder+'/'+str(Path(image_path).name))
    #         image_label = get_bbox(completion,self.cls2number)
    #         file = open(f'{label_folder}/{Path(image_path).stem}.txt','w') 
    #         for cls, x, y, w, h in image_label:
    #             file.write(f'{cls} {x} {y} {w} {h}')
    #         file.close()
    #         dict_file = {
    #                     'nc': len(self.labels),
    #                     'names': self.labels,
    #                     'train': image_folder,
    #                     'val': image_folder,
    #                     }
    #         with open(str(Path(image_folder).parent)+'/data.yaml', 'w') as file:
    #             documents = yaml.dump(dict_file, file)
    #         print('#####################'*10)
    #         # updata every annotations each time bug?
    #         yolov5train.run(batch=self.batch_size, epochs=self.epochs, data='./data.yaml', imgsz=512, weights='./best.pt', cfg='./yolov5/models/yolov5s.yaml', project='cosmetic_auto_label_model', name=datetime.now().strftime('%y_%m_%d_%H_%M_%S'))
            
    #     return {'model_file': 'model_file'}