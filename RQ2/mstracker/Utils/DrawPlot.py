import pandas as pd
import matplotlib.pyplot as plt

fig, ax = plt.subplots()

# hide axes
fig.patch.set_visible(False)
ax.axis('off')
ax.axis('tight')

f = pd.read_csv("/Users/sense/Degree/Util/CSV/statistic_log_info_table.csv")
test_df = f.IsTestfile.str.contains('Yes')
test_f = f[test_df]
production_df = f.IsTestfile.str.contains('No')
production_f = f[production_df]

total_row = ['Total', f["LoggingNum"].sum(), f["AssertNum"].sum(), f["StackTraceNum"].sum(), f["PrintlnNum"].sum(), f["SlocNum"].sum()]
test_row = ['Test', test_f["LoggingNum"].sum(), test_f["AssertNum"].sum(), test_f["StackTraceNum"].sum(), test_f["PrintlnNum"].sum(), test_f["SlocNum"].sum()]
production_row = ['Production', production_f["LoggingNum"].sum(), production_f["AssertNum"].sum(), production_f["StackTraceNum"].sum(), production_f["PrintlnNum"].sum(), production_f["SlocNum"].sum()]


df = pd.DataFrame([total_row, test_row, production_row], columns=['', 'Logging', 'Assert', 'StackTrace', 'Println', 'Sloc'])

ax.table(cellText=df.values, colLabels=df.columns, loc='center', cellLoc='center')

fig.tight_layout()

plt.show()
