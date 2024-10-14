import difflib

FILES = [
    "test_pred_test_dataset.csv",
    "test_pred_train_dataset.csv",
    "y_pred_test_dataset.csv",
    "y_pred_train_dataset.csv",
]

def files_content_is_equal(file1, file2):    
    with open(file1, 'r') as f1, open(file2, 'r') as f2:
        # Read lines from both files
        f1_lines = f1.readlines()
        f2_lines = f2.readlines()

        # Use difflib to compare the lines
        diff = difflib.unified_diff(f1_lines, f2_lines, fromfile=file1, tofile=file2)

        # Print the differences
        different = True
        for line in diff:
            different = False 
            print(line, end='')            
        return different


# Compare result files
print("---------------------------------------------------------------------------------------------------------------")
print("                                 RESULT FILES COMPARISON")
print("---------------------------------------------------------------------------------------------------------------")

# Compare results files with expected
files_are_equal = True
for file in FILES:
    expected_results_file = f"test_models/expected_results/{file}" 
    if not files_content_is_equal(file, expected_results_file):
        files_are_equal = False
        print(f"Differnece in file {file}")

if files_are_equal:
    print("Result files are equal to expected results files !")
