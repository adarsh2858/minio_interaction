import os, sys, argparse
from minio import Minio
from minio.error import (ResponseError, BucketAlreadyOwnedByYou,
                            BucketAlreadyExists)

parser = argparse.ArgumentParser(description="Give inputs via cmd:")
#-n Mock Test No. -u USERNAME -d Directory Name -s Text file name
parser.add_argument("-id", type=str, help="the course name for mock test number")
parser.add_argument("-u", metavar='U',  help="Username")
parser.add_argument("-d", help="Directory name (where the user-answers are stored)")

args = parser.parse_args()
minioClient = Minio(os.environ['SERVER_NAME'],
                   access_key=str(os.environ['ACCESS_KEY']),
                   secret_key=str(os.environ['SECRET_KEY']),
                   secure=False)

class my_class:    
    # Taking inputs for refining the folder structure
    bucket_name = 'mock-exams'
    mockTestID=args.id
    username =args.u
    shellCmdFile = 'commandsToExecute'

    # Following code just returns the filename not location
    # user's answer files to be pushed to minio
    dirName = args.d
    arr = os.listdir(dirName)

    def makeBucket(self):
        try:            
            minioClient.make_bucket(self.bucket_name)

        except BucketAlreadyOwnedByYou as err:
            pass
        except BucketAlreadyExists as err:
            pass
        except ResponseError as err:
            print(err)
        return

    def readAndExecuteTextFile(self):
        try:
            object_name = "Course "+str(self.mockTestID)+"/"+self.shellCmdFile+".txt"
            file_path = self.shellCmdFile+".txt"                    
            minioClient.fget_object(self.bucket_name, object_name, file_path)   # Code to put files into the folder in bucket of corresponding user
            
            with open(self.shellCmdFile+".txt") as f:
                for line in f:
                    os.system(line)

        except ResponseError as err:
            print(err)
        except:
            parser.print_help()
        return

    def pushToMinio(self):
        # Now we need a for loop to iterate through the list containing all files from a particular directory
        try:
            for each in self.arr:
                object_name = "Course "+str(self.mockTestID)+ '/user-'+self.username+"/" +each  
                file_path = os.path.join(self.dirName, each)                
                minioClient.fput_object(self.bucket_name, object_name, file_path)   # Code to put files into the folder in bucket of corresponding user
            
        except FileNotFoundError:
            print("File is missing contact support !")
        except ResponseError as err:
            print(err)
        except:
            parser.print_help()
        return

instance = my_class()
instance.makeBucket()
instance.readAndExecuteTextFile()
instance.pushToMinio()
