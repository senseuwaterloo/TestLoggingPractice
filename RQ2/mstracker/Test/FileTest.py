import re

from Utils import FileUtil
import os

# for root, dirs, files in os.walk(os.path.abspath("/Users/sense/Degree/VCS/hadoop")):
#     for file in files:
#         if FileUtil.is_test_file(os.path.join(root, file)):
#             print(os.path.join(root, file) + ": " + str(FileUtil.is_test_file(os.path.join(root, file))))
#             print(os.path.basename(os.path.join(root, file)))

# print(FileUtil.is_test_file("src/core/org/apache/hadoop/fs/s3native/NativeS3FileSystemContractBaseTest.java"))

pattern = '^[Mm]ock|[Mm]ock$|.*[Tt]est.*'
match = re.search(pattern, "TestGlobalFilter")
print(match)
