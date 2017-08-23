import swiftclient
import os


auth_url =
projectId = 
region = 
userId = 
password = 



def authenticate():
    return swiftclient.Connection(key=password, authurl=auth_url, auth_version='3',
                                      os_options={"project_id": projectId, "user_id": userId, "region_name": region})


def createContainer():
    container_name = 'file-container'
    Obj_conn = authenticate()
    Obj_conn.put_container(container_name)
    return Obj_conn


def getContainerName(Obj_conn):
    for container in Obj_conn.get_account()[1]:
        return container['name']


def upload():
    file_type = ['txt', 'TXT', 'text','jpg','jpeg','JPG', 'pdf','PDF']
    root = 'container/'
    Obj_conn = createContainer()
    container_name = getContainerName(Obj_conn)

    for dirName, subdirList, fileList in os.walk(root):
        for fname in fileList:
            if fname[-3:] in file_type:
                file_location = (dirName + "/" + fname)
                with open(file_location, 'rb') as load_file:
                    Obj_conn.put_object(container_name, fname, contents=load_file.read(), content_type='mime_type')
                    load_file.close()
    return 'Upload Successful!'



def list_files():
    root = 'container/'
    filenames = []
    for (dirName, subdirList, fileList) in os.walk(root):
        filenames.extend(fileList)

    return filenames



def download():
    Obj_conn = createContainer()
    container_name = getContainerName(Obj_conn)
    filename = 'input.txt'
    file_details = Obj_conn.get_object(container_name, filename)
    with open('download.txt', 'wb') as my_copy:
        my_copy.write(file_details[1])
    return filename + ' Downloaded!'


if __name__ == '__main__':
    upload()