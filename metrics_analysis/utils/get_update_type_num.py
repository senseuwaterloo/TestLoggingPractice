import pandas as pd

log_csv = pd.read_csv("path_to_ms_log.csv")

log_call_df = log_csv[log_csv["call_type"] == "LOG_CALL"]
print_call_df = log_csv[log_csv["call_type"] == "PRINT_CALL"]
monitoring_call_df = pd.concat([log_call_df, print_call_df], axis=0)

update_log_df = monitoring_call_df[monitoring_call_df["change_type"] == "UPDATED"]

test_update_log_df = update_log_df[update_log_df["is_test_log"] == "t"]
production_update_log_df = update_log_df[update_log_df["is_test_log"] == "f"]


test_update_format = test_update_log_df[test_update_log_df["update_type"].str.contains("UPDATED_FORMAT", na=False)]
test_update_verbosity = test_update_log_df[test_update_log_df["update_type"].str.contains("UPDATED_VERBOSITY", na=False)]
test_update_method = test_update_log_df[test_update_log_df["update_type"].str.contains("UPDATED_LOGGING_METHOD", na=False)]
test_update_text = test_update_log_df[test_update_log_df["update_type"].str.contains("TEXT", na=False)]
test_update_var = test_update_log_df[test_update_log_df["update_type"].str.contains("VAR", na=False)]
test_update_sim = test_update_log_df[test_update_log_df["update_type"].str.contains("SIM", na=False)]

production_update_format = production_update_log_df[production_update_log_df["update_type"].str.contains("UPDATED_FORMAT", na=False)]
production_update_verbosity = production_update_log_df[production_update_log_df["update_type"].str.contains("UPDATED_VERBOSITY", na=False)]
production_update_method = production_update_log_df[production_update_log_df["update_type"].str.contains("UPDATED_LOGGING_METHOD", na=False)]
production_update_text = production_update_log_df[production_update_log_df["update_type"].str.contains("TEXT", na=False)]
production_update_var = production_update_log_df[production_update_log_df["update_type"].str.contains("VAR", na=False)]
production_update_sim = production_update_log_df[production_update_log_df["update_type"].str.contains("SIM", na=False)]

print("test:")
print(len(test_update_format))
print(len(test_update_verbosity))
print(len(test_update_method))
print(len(test_update_text))
print(len(test_update_var))
print(len(test_update_sim))

print("production:")
print(len(production_update_format))
print(len(production_update_verbosity))
print(len(production_update_method))
print(len(production_update_text))
print(len(production_update_var))
print(len(production_update_sim))

