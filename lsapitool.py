import requests
import json

class Base:
    def __init__(self, token, url):
        self.token = token
        self.url = url

    def get_token(self):
        return self.token

    def get_url(self):
        return self.url

    def get_projects_info(self):
        '''
        https://labelstud.io/api#section/Authentication
        '''
        uri = '/api/projects/'
        headers = {"Authorization": f"Token {self.token}"}
        r = requests.get(self.url+uri, headers=headers)
        if r.status_code == 200:
            data = json.loads(r.text)
            return data
        else:
            return None

    def create_new_project(self, title, label_config):
        '''
        https://labelstud.io/api#operation/api_projects_create
        label_config = "<View>[...]</View>"
        '''
        uri = '/api/projects'
        headers = {"Authorization": f"Token {self.token}",
                   "Content-Type": "application/json"}
        data = {"title": title,
                "label_config": label_config}   
        r = requests.post(self.url+uri, data=json.dumps(data),headers=headers)
        if r.status_code == 201:
            data = json.loads(r.text)
            return data
        else:
            print(r.status_code)
            return None
    
    def delete_project(self, project_id):
        '''
        https://labelstud.io/api#operation/api_projects_delete
        '''
        uri = f'/api/projects/{project_id}/'
        headers = {"Authorization": f"Token {self.token}"}
        r = requests.delete(self.url+uri, headers=headers)
        if r.status_code == 204:
            return True
        else:
            print(r.status_code)
            return None
    
    
    def create_new_task(self, project_id, data, annotations=None):
        '''
        https://labelstud.io/api#operation/api_tasks_create
        '''
        uri = '/api/tasks'
        headers = {"Authorization": f"Token {self.token}",
                   "Content-Type": "application/json"}
        data = {"project":project_id, "data": data, "annotations": annotations,}
        r = requests.delete(self.url+uri, headers=headers)
        if r.status_code == 201:
            data = json.loads(r.text)
            return data
        else:
            print(r.status_code)
            return None

if __name__ == '__main__':
    token = '55de8e4ac26a70f1749eb0c9d9000e4ebf24d503'
    url = 'http://127.0.0.1:8080'
    base = Base(token=token, url=url)

    results = base.get_projects_info()['results']
    for res in results:
        print(res['title'])

    # title = 'test'
    # label_config = '''
    # <View>
    #     <Image name="image" value="$image"/>
    #     <RectangleLabels name="label" toName="image">
    #         <Label value="Airplane" background="green"/>
    #         <Label value="Car" background="blue"/>
    #     </RectangleLabels>
    # </View>
    # '''
    # results = base.create_new_project(title,label_config)
    # print(results['id'], results['title'])

    # print(base.delete_project(results['id']))