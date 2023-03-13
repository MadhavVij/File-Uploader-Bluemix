import base64
import json

import pymysql
import swiftclient
import os

from cloudant import Cloudant
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from flask import Flask, render_template, jsonify
from cryptography.fernet import Fernet

#Object Storage Credentials
auth_url = 
projectId = 
region = 
userId = 
password = 

#Cloudant Credentials
cloud_username = 
cloud_password = 
cloud_url = 

client = Cloudant(cloud_username, cloud_password, url=cloud_url)
client.connect()
session = client.session()




app = Flask(__name__)


def genKey():
    passWord= input('Enter key: ')
    salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    passWord = passWord.encode()
    return base64.urlsafe_b64encode(kdf.derive(passWord))




def authenticate():
    return swiftclient.Connection(key=password, authurl=auth_url, auth_version='3',
                                      os_options={"project_id": projectId, "user_id": userId, "region_name": region})


def createContainer(container_name):
    #container_name = 'file-container'
    #container_name2 = 'file-container2'
    #container_name3 = 'file-container3'
    Obj_conn = authenticate()
    Obj_conn.put_container(container_name)
    #Obj_conn.put_container(container_name2)
    return Obj_conn


def getContainerName(Obj_conn):
    for container in Obj_conn.get_account()[1]:
        return container['name']


def createDB():
    dbName = "datafiles"
    return client.create_database(dbName)


@app.route('/toCloudUp')
def cloudList():
    root = app.root_path + '\container/'
    filenames = []
    for (dirName, subdirList, fileList) in os.walk(root):
        filenames.extend(fileList)
    return render_template('toCloudUp.html', files=filenames)


@app.route('/cloudUp')
def cloudantUpload():
    #dbName = "datafiles"
    #dbName = client[dbName]
    #filePath = app.root_path+'\container/'+filename
    #f = open(filePath,'rb')
    #data = f.read()
    dbName = "datafiles"
    dbName = client[dbName]
    data = ListLocal()
    #jdata = json.load(data)
    #jdata = jdata[0]
    print(data[0])
    dbName.create_document({data[0]})
    #dbName.create_document({zerocount:[{filename: data.decode()}]})
    return 'Uploaded Successful!'


@app.route('/upload')
def upload():
    file_type1 = ['txt', 'TXT', 'text']
    file_type2 = ['jpg','jpeg','JPG','JPEG','png','PNG','gif']
    root = app.root_path + '\container/'


    for dirName, subdirList, fileList in os.walk(root):
        for fname in fileList:
            file_location = f"{dirName}/{fname}"
            size = os.path.getsize(file_location)

            if fname[-3:] in file_type1:
                container_name = 'file-container'
                Obj_conn = createContainer(container_name)

                with open(file_location, 'rb') as load_file:
                    Obj_conn.put_object(container_name, fname, contents=load_file.read(),
                                        content_type='application/octet-stream')
                    load_file.close()

            elif fname[-3:] in file_type2 or fname[-4:] in file_type2:
                container_name = 'small_img' if size <= 200000 else 'large_img'
                Obj_conn = createContainer(container_name)
                file_location = f"{dirName}/{fname}"
                with open(file_location, 'rb') as load_file:
                    Obj_conn.put_object(container_name, fname, contents=load_file.read(),
                                        content_type='application/octet-stream')
                    load_file.close()

    return 'Upload Successful!'


@app.route('/files')
def list_files():
    print(app.root_path)
    root = app.root_path+'\container/'
    filenames = []
    for (dirName, subdirList, fileList) in os.walk(root):
        filenames.extend(fileList)
    print(filenames)
    return render_template('files.html', files=filenames)


@app.route('/toDownload')
def downloadList():
    Obj_conn = createContainer()
    container_name = getContainerName(Obj_conn)
    filenames = [
        data['name'] for data in Obj_conn.get_container(container_name)[1]
    ]
    return render_template('toDownload.html', files=filenames)


@app.route('/download/<filename>')
def download(filename):
    Obj_conn = createContainer()
    container_name = getContainerName(Obj_conn)
    file_details = Obj_conn.get_object(container_name, filename)
    with open(app.root_path+'\download.txt', 'wb') as my_copy:
        my_copy.write(file_details[1])
    return f'{filename} Downloaded!'


@app.route('/toEncrypt')
def encryptList():
    root = app.root_path + '\container/'
    filenames = []
    for (dirName, subdirList, fileList) in os.walk(root):
        filenames.extend(fileList)
    return render_template('toEncrypt.html', files=filenames)


@app.route('/encrypt/<userFile>')
def encryptFile(userFile):
    key = genKey()
    root = app.root_path
    f = open(f'{root}/{userFile[:-4]}_key.txt', 'wb')
    f.write(key)
    f = Fernet(key)

    for dirName, subdirList, fileList in os.walk(f'{root}/container/'):
        for fname in fileList:
            if userFile == fname:
                file_location = f"{dirName}/{fname}"
                with open(file_location, 'rb') as load_file:
                    token = f.encrypt(load_file.read())
                    load_file.close()

                fname = f'{fname[:-4]}-crypted{fname[-4:]}'
                new_location = f"{root}/encrypted/{fname}"
                with open(new_location, 'wb') as write_file:
                    write_file.write(token)
                    write_file.close()

    return f'file {fname} encrypted'


@app.route('/toDecrypt')
def decryptionList():
    root = app.root_path + '\encrypted/'
    filenames = []
    for (dirName, subdirList, fileList) in os.walk(root):
        filenames.extend(fileList)
    return render_template('toDecrypt.html', files=filenames)


@app.route('/decrypt/<userFile>')
def decryptFile(userFile):
    root = app.root_path
    userFile = userFile[:-12]+userFile[-4:]
    f = open(f'{root}/{userFile[:-4]}_key.txt', 'rb')
    key = f.read()
    g = Fernet(key)

    for dirName, subdirList, fileList in os.walk(f'{root}/encrypted/'):
        for fname in fileList:
            if f'{userFile[:-4]}-crypted{userFile[-4:]}' == fname:
                file_location = f"{dirName}/{fname}"
                with open(file_location, 'rb') as load_file:
                    token = g.decrypt(load_file.read())
                    load_file.close()

                fname = f'{userFile[:-4]}-decrypted{userFile[-4:]}'
                new_location = f"{root}/decrypted/{fname}"
                print(new_location)
                with open(new_location, 'wb') as write_file:
                    write_file.write(token)
                    write_file.close()

    return f'file {fname} decrypted'


@app.route('/')
def Welcome():
    return render_template('index.html')


def connectDB():
    host = ''
    port = 3306
    user = ''
    password = ''
    db = ''
    return pymysql.connect(
        host=host, port=port, user=user, password=password, db=db
    )


@app.route('/clearUp')
def uploadFile():
    conn = connectDB()
    curr = conn.cursor()
    file_type1 = ['txt', 'TXT', 'text']
    file_type2 = ['jpg', 'jpeg', 'JPG', 'JPEG', 'png', 'PNG', 'gif']
    root = app.root_path + '\container/'

    for dirName, subdirList, fileList in os.walk(root):
        for fname in fileList:
            file_location = f"{dirName}/{fname}"
            fsize = os.path.getsize(file_location)

            if fname[-3:] in file_type1:
                with open(file_location, 'rb') as load_file:
                    fdata = load_file.read()

                query = 'insert into file_container (fname,fsize, fdata) VALUES (%s,%s,%s)'
                args = (fname,fsize,fdata)
                curr.execute(query,args)
                conn.commit()
                load_file.close()
    # results = curr.fetchall()
    # for row in results:
    #     print(row[1])
    # conn.commit()
    curr.close()
    conn.close()
    return 'DB Updated!'

@app.route('/clearDown/<filename>')
def downloadFile(filename):
    conn = connectDB()
    curr = conn.cursor()
    query = 'select fdata from file_container WHERE fname = %s'
    args = (filename)
    curr.execute(query, args)
    fdata =  curr.fetchone()[0]
    with open(app.root_path + '\download.txt', 'wb') as my_copy:
        my_copy.write(fdata)
    conn.commit()
    curr.close()
    conn.close()
    return f'Downloaded {filename}'


####################################################
@app.route('/ListLocal')
def ListLocal():
    root = app.root_path
    filenames = []
    zerocount = 0
    for dirName, subdirList, fileList in os.walk(f'{root}/container/'):
        for fname in fileList:
            file_location = f"{dirName}/{fname}"
            size = os.path.getsize(file_location)
            if size == 0:
                zerocount += 1
            filenames.append((fname, size))
    dbName = "datafiles"
    dbName = client[dbName]
    zerocount = [zerocount]
    for filename,size in filenames:
        file_location = f'{root}/container/{filename}'
        with open(file_location, 'rb') as load_file:
            data = load_file.read()
        data = data.decode('utf-8')
        zerocount.append({filename: data})
    return jsonify(zerocount)




port = os.getenv('PORT', '5000')
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=int(port))