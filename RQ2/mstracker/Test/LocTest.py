from Utils import LocUtil

# dict_test = LocUtil.get_java_loc_diff("/Users/sense/Desktop/diff/AbfsRestOperation.java", "/Users/sense/Desktop/diff/AbfsRestOperation_after.java")
# print(str(dict_test['added'].code_num))
# print(str(dict_test['removed'].code_num))
# print(str(dict_test['modified'].code_num))

# print(LocUtil.get_java_sloc("/Users/sense/Desktop/diff/AbfsRestOperation.java"))
LocUtil.get_java_loc_diff("/Users/sense/Degree/VCS/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractRootDirectoryTest.java", "/Users/sense/Degree/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractRootDirectoryTest.java")
