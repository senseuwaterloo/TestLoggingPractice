
# caller_method = "log.warn('test')".split('(')[0]
# print(caller_method)
# caller_method = ''.join(caller_method.split())
# print(caller_method)
# verbosity = caller_method.split('.')[-1]
# print(verbosity)
# caller_object = caller_method.rsplit('.', 1)[0]
# print(caller_object)
import sys

from Models.Log import Log
from Models.Log import LogChangeType
from Profilers import LogProfiler

# log = Log.create(commit=2, file_path='hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/s3guard/S3Guard.java',
#                  embed_method='logS3GuardDisabled(Logger,String,String)',change_type=LogChangeType.UPDATED,
#                  content='LOG.warn("Failed to renew lease for " + clientName + " for "\n              + (elapsed/1000) + " seconds (>= hard-limit ="\n              + (dfsClientConf.getleaseHardLimitPeriod() / 1000) + " seconds.) "\n              + "Closing all files being written ...", e)',
#                  content_update_from='LOG.warn("Failed to renew lease for " + clientName + " for "\n              + (elapsed/1000) + " seconds (>= hard-limit ="\n              + (HdfsConstants.LEASE_HARDLIMIT_PERIOD / 1000) + " seconds.) "\n              + "Closing all files being written ...", e)',
#                  verbosity='warn', verbosity_type='WARN', argument_type='TEXT_VAR_SIM')
# sys.setrecursionlimit(2000)
log = Log.create(commit=2, file_path='hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/s3guard/S3Guard.java',
                 embed_method='logS3GuardDisabled(Logger,String,String)',change_type=LogChangeType.UPDATED,
                 content='assertNotNull("No test filesystem", fileSystem)',
                 content_update_from='assertNotNull("No test filesystem")',
                 verbosity='warn', verbosity_type='WARN', argument_type='TEXT_VAR')

print(LogProfiler.get_log_update_detail(log))
print(sys.getrecursionlimit)
