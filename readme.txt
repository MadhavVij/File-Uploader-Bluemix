Name: Madhav Vij
Project: File Uploader
Programming Lang: Python 3.6
*********

-----INSTRUCTIONS-----
## Create IBM Bluemix Profile
## Add authetication variables in file_uploader.py
## Run the program


*********



*********
CODE_STRUCTURE

File: file_uploader.py
#	authenticate()
		It authenticates the user with IBM Bluemix credentials, whenever required
#	createContainer()
		It initiallizes container for file storage in IBM Bluemix
#	getContainerName(Obj_conn)
		Outputs the container name for the given Object
#	upload()
		Upload files to the container in IBM Bluemix
#	list_files()
		Displays a list of filenames present in the container
#	download()
		Downloads the files to a pre determined location on user's machine
#	genKey()
		generates random string from user's input
#	createDB()
		create Database in Cloudant
# 	connectDB()
		connect to Cloudant DB using IBM credentials
#	cloudantUpload()
		Upload files to Coudant Database
#	encryptFile()
		encrypt files (SHA-256) in given directory
#	decryptFile(userFile)
		decrypt provided files and add them to pre determined directory

*********