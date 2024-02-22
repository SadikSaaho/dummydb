import os, json, sys
from feature_grouping_type import Feature_Grouping_Obj
from AC_Obj import AC
from AT_Obj import AT
import shutil

# JSON path
config_info = r"W:\Repo\gwt_db\JSON_File\Test_Automation_Pipeline.json"

# Obtain the JSON
with open(config_info, "r") as f:
    json_obj = json.loads(f.read())

# Import universal library
sys.path.append(json_obj["universal_repo_folder"])
from Libs_Coordinator import Universal_Library # NOTE the UL is currently only used to search for & import GWT functions, not other utility functions

class GWT_TOOLKIT:
    def __init__(self, start_rec_func, stop_rec_func, mp_lib_user, mp_lib_base):
        print("Initializing GWT tk")
        if json_obj["lab_file_path"] == "":
            lab = None
        else:
            lab = json_obj["lab_file_path"]
        print(f"lab: {lab}")

        if json_obj["FSM_path"] == "":
            fsm = None
        else:
            fsm = json_obj["FSM_path"]
        print(f"fsm: {fsm}")

        if json_obj["RA_table_path"] == "":
            ra = None
        else:
            ra = json_obj["RA_table_path"]
        print(f"ra: {ra}")

        # Variables to hold the start & stop recording functions for all of the environments
        self.start_recording_function = start_rec_func
        self.stop_recording_function = stop_rec_func

        # Define self.mp_lib_user NOTE this will be deprecated once the UL is implemented
        self.mp_lib_user = mp_lib_user
        self.mp_lib_base = mp_lib_base

        # Create a boolean variable which tells us if the last structure that was iterated through was a background or AT
        self.is_AT = None

        self.Obtain_inputs(BTS_md_path = json_obj["BTS_path"], Recordings = json_obj["Recordings_folder"], univ_repo_path = json_obj["universal_repo_folder"], Lab_path = lab, FSM_path = fsm, RA_table = ra, test_env_type = json_obj["test_environment"], comp_lib_type = json_obj["component_library"], comp_sub_lib_type = json_obj["component_sub_library"])

    def Obtain_inputs(self, BTS_md_path, Recordings, univ_repo_path, test_env_type, comp_lib_type, comp_sub_lib_type, Lab_path = None, FSM_path = None, RA_table = None):
        print("Obtaining inputs")
        #### Create instances to hold the types of Testing Environment, Component Library, Component Sub-Library
        # self.Test_Env = None
        # self.Comp_Lib = None
        # self.Comp_Sub_Lib = None

        #### Create an instance of Universal Library
        # self.univ_lib = Universal_Library(universal_repo_path = univ_repo_path)

        #### Create a JSON variable to hold the summary from the feature groupings
        self.JSON_Summary = {}
        
        #### Create a variable that holds the BTS title ####
        self.BTS_title = None
        
        #### Create a list that holds the feature groupings ####
        self.feature_groupings = []

        #### Obtain the Recordings path ####
        self.Recordings_path = Recordings

        #### Obtain the BTS ####
        self.BTS_md_file = BTS_md_path

        #### Obtain the testing env ####
        self.Test_Env = test_env_type

        #### Obtain the componment library  ####
        self.Comp_Lib = comp_lib_type

        #### Obtain the componment sub library  ####
        self.Comp_Sub_Lib = comp_sub_lib_type

        if RA_table:
            #### Obtain the RA table file ####
            self.RA_table_file = RA_table

        if Lab_path:
            #### Obtain the .lab file ####
            self.lab_file = Lab_path

        if FSM_path:
            #### Obtain the FSM file ####
            self.FSM_file = FSM_path

    def Fill_Feature_Groupings(self, BTS_path):
        print("Filling feature groupings")
        with open(BTS_path, "r") as file:
            lines = file.readlines()
            # try:
            # Grab the title of the BTS
            if lines[0].endswith("\n"):
                self.BTS_title = lines[0][:-1]
                # self.BTS_title = self.BTS_title[:-1] # Done twice to remove both "\" and "n"
            else:
                self.BTS_title = lines[0]

            for line in lines:

                # Removing the trailing space from the string
                line = line.rstrip("\n")

                # self.append_log(f"Statements: {line}")
                # Check the status of the brake since it should be released right now

                # Check if the loop has encountered a feature grouping
                if "Feature Grouping" in line:
                    fg_num = line.split(" ")[3].split(":")[0]
                    fg_name = line.split("`")[-2]

                    # Append the current feature grouping to the list of feature groupings
                    self.feature_groupings.append(Feature_Grouping_Obj(name = fg_name, ID = fg_num))

                # # Check if the loop has encountered a Testing Environment, Component Library, or Component Sub Library declaration
                # if "Testing Environment:" in line: # TODO validate this 
                #     self.Test_Env = line.split("Component Library: ")[1]

                # if "Component Library:" in line:
                #     self.Comp_Lib = line.split("Component Library: ")[1]

                # if "Component Sub-Library:" in line:
                #     self.Comp_Sub_Lib = line.split("Component Sub-Library: ")[1]

                # If the line has "### Rule" in it obtain the AC number and name
                if "### Rule" in line:
                    rule_num = line.split(" ")[2].split(":")[0]
                    rule_name = line.split("`")[-2]

                    # Enter the rule/AC in the feature grouping obj
                    AC_object = AC(ID = rule_num, name = rule_name)
                    self.feature_groupings[-1].enter_rule(rule_ID = AC_object.get_rule_ID(), AC_obj = AC_object)

                if "#### Scenario" in line:
                    scenario_num = line.split(" ")[2].split(":")[0]
                    scenario_name = line.split("`")[-2]

                    # Get the Absolute Path
                    abs_path = f"FG{fg_num}_R{rule_num}_S{scenario_num}"

                    # Set the self.is_AT variable to True since we just passed a scenario
                    self.is_AT = True

                    # Enter the scenario/AT in the feature grouping obj
                    AT_object = AT(ID = scenario_num, name = scenario_name, abs_path = abs_path)
                    self.feature_groupings[-1].get_latest_rule().enter_scenario(scenario_ID = AT_object.get_Scenario_ID(), AT_obj = AT_object)

                if "### Background" in line:
                    # Set the self.is_AT variable to False since we just passed a background
                    self.is_AT = False

                if ("Given: " in line) or ("When: " in line) or ("Then: " in line) or ("AND: " in line):
                    # Grab the statement type (given or when or then)
                    stmnt_type = line.split(" ")[0][:-1]

                    # This declaration below removes any ; and , and \n from the statement if it's there
                    stmnt_contents = line.split(f"{stmnt_type}: ")[1].replace(";", "").replace(",", "").replace("\n", "") # NOTE This might need improving for robustness
                    if stmnt_contents.endswith("."):
                        stmnt_contents = stmnt_contents[:-1]

                    print(f"Encountered a {stmnt_type} statement with contents: {stmnt_contents}")

                    # Filter the statement and add GWT_ to it
                    # filtered_stmnt, stmnt_inputs = self.Statement_Filter(gwt_stmnt = stmnt_contents)

                    # Obtain the statement function TODO complete the process of getting env, comp & sub_comp
                    statement_function, stmnt_inputs = self.Function_Runner(gwt_stmnt = stmnt_contents, mp_lib_user = self.mp_lib_user, mp_lib_base = self.mp_lib_base)
                    # self.univ_lib(func_name = filtered_stmnt, env = self.Test_Env, comp = self.Comp_Lib, sub_comp = self.Comp_Sub_Lib)

                    # If the last type was a scenario then add the statement to the scenario obj. Else, add the statement to the background of the scenario obj
                    if self.is_AT: # If AT
                        # Create a statement based on the statement type and contents and add it to the rules list in the latest feature grouping
                        self.feature_groupings[-1].get_latest_rule().get_latest_scenario().enter_statement(statement_type = stmnt_type, statement_contents = stmnt_contents, statement_function = statement_function, statement_inputs = stmnt_inputs)
                    else: # If background
                        print("Adding background to FG")
                        if stmnt_inputs:
                            self.feature_groupings[-1].get_latest_rule().set_background(stmnt_type = stmnt_type, stmnt_contents = stmnt_contents, stmnt_func = statement_function, stmnt_inputs = stmnt_inputs)
                        else:
                            self.feature_groupings[-1].get_latest_rule().set_background(stmnt_type = stmnt_type, stmnt_contents = stmnt_contents, stmnt_func = statement_function)

        return self.feature_groupings

    def Function_Runner(self, gwt_stmnt, mp_lib_user, mp_lib_base): # gwt_stmnt form: "set ZF fault A"
        # Split the gwt_stmnt into a list of seperate words
        words_lst = gwt_stmnt.split(" ")
        captured_inputs_lst = []
        filtered_words_lst = []
        letters_lst = ["F", "E", "D", "C", "B", "A"]

        # Filter the words_lst and use it to fill up the filtered_words_lst: if there're inputs, gather them and put them in a list, place underscores between the words, 
        # replace the inputs (marked with a number of a var that has underscores in it) with A, B, C, etc.
        for word in words_lst:
            if "_" in word or word.isnumeric():
                # Place the inputs in a list
                if word.isnumeric():
                    captured_inputs_lst.append(float(word))
                else:
                    captured_inputs_lst.append(word)
                
                # Place a letter in the place of the input in the filtered_words_lst
                filtered_words_lst.append(letters_lst.pop())
            else:
                filtered_words_lst.append(word)
        gwt_stmnt_fltrd = ("_").join(filtered_words_lst)

        # Adding GWT_ to the front of the statement since the GWT statements in mp_lib_base.py start with GWT_ TODO test this out
        gwt_stmnt_fltrd = "GWT_" + gwt_stmnt_fltrd

        # Gathering the libraries from mp_lib_user.py
        mp_lib_list = mp_lib_user.get_mp_lib_list()
        # self.append_log(dir(mp_lib_list[0]))
        
        # Iterate through the libs to see if the function is in them. If it is, return the function. Else, return a message mentioning that the current scenario isn't valid
        for lib in mp_lib_list:
            if hasattr(mp_lib_base, gwt_stmnt_fltrd): # First check if the func is in mp_lib_base
                # self.mp_lib_base.gwt_stmnt_fltrd(*captured_inputs_lst)
                # if "_" in gwt_stmnt_fltrd:
                #     self.mp_lib_base._load_dictionary()
                
                # Load up the dict in the class
                self.mp_lib_base._load_dictionary()

                func_to_run = getattr(self.mp_lib_base, gwt_stmnt_fltrd)
                # mp_lib_func_status = func_to_run(*captured_inputs_lst)
                return func_to_run, captured_inputs_lst
            
            elif hasattr(lib, gwt_stmnt_fltrd):
            # if gwt_stmnt_fltrd in dir(lib): # check if the gwt_stmnt_fltrd (function form) is in the lib
                # lib.gwt_stmnt_fltrd(*captured_inputs_lst)

                # Load up the dict in the class
                lib._load_dictionary()

                func = getattr(lib, gwt_stmnt_fltrd)
                # lib_func_status = func(*captured_inputs_lst)
                return func, captured_inputs_lst
            else:
                raise RuntimeError(f"The GWT statement {gwt_stmnt_fltrd} isn't in the libraries")

    def Execute_GWT_Scenarios(self):
        print("Executing GWT Scenarios")
        # Create a dict that'll be inside of self.JSON_summary to hold the FG objects
        FGs_dict = {}
        fg_num = 1

        # Iterate through the feature groupings list and execute all the statements in the scenarios (ATs)
        for feature_grouping in self.feature_groupings:
            feature_grouping.Execute_Feature_Grouping(start_rec_func = self.start_recording_function, stop_rec_func = self.stop_recording_function, stmnt_paths = self.stmnt_paths)
            fg_name = feature_grouping.get_FG_name()
            fg_summary = feature_grouping.get_FG_summary()
            fg_title = f"Feature Grouping {fg_num}"
            FGs_dict[fg_title] = {fg_name:fg_summary} #added feature grouping title to json
            fg_num += 1
 
        # Fill in the self.JSON_Summary variable
        self.JSON_Summary["BTS Title"] = self.BTS_title
        self.JSON_Summary["Feature Groupings"] = FGs_dict

    def Statement_Filter(self, gwt_stmnt): # gwt_stmnt form: "set ZF fault A" NOTE remove when Function_Runner is validated
        # Split the gwt_stmnt into a list of seperate words
        words_lst = gwt_stmnt.split(" ")
        captured_inputs_lst = []
        filtered_words_lst = []
        letters_lst = ["F", "E", "D", "C", "B", "A"]

        # Filter the words_lst and use it to fill up the filtered_words_lst: if there're inputs, gather them and put them in a list, place underscores between the words, 
        # replace the inputs (marked with a number of a var that has underscores in it) with A, B, C, etc.
        for word in words_lst:
            if "_" in word or word.isnumeric():
                # Place the inputs in a list
                if word.isnumeric():
                    captured_inputs_lst.append(float(word))
                else:
                    captured_inputs_lst.append(word)
                
                # Place a letter in the place of the input in the filtered_words_lst
                filtered_words_lst.append(letters_lst.pop())
            else:
                filtered_words_lst.append(word)
        gwt_stmnt_fltrd = ("_").join(filtered_words_lst)

        # Adding GWT_ to the front of the statement since the GWT statements in mp_lib_base.py start with GWT_ TODO test this out
        gwt_stmnt_fltrd = "GWT_" + gwt_stmnt_fltrd
        return gwt_stmnt_fltrd, captured_inputs_lst

    def Generate_Reports(self):
        print("Generating reports")
        with open(config_info, "w") as file:
            # Update the json_obj with the results
            json_obj["Results"] = self.JSON_Summary
            json.dump(json_obj, file)

    def Generate_Results_Structure(self):
        # Go to the location saved in self.Recordings_path and iterate through the FGs to create folders of FGs, ACs, and ATs. 
        # Store the GWT Stmnts recordings in the AT folders. Create a dict to hold the statement paths to store the recordings
        # in them later
        print("Generating Results Structure")
        self.stmnt_paths = {} # The dict to hold all of the statement paths

        os.chdir(self.Recordings_path) # Go to the recordings path to set up the structure

        if not len(os.listdir(self.Recordings_path)) == 0: # If there exist recordings from prior tests, delete them
            folders = os.listdir()
            for folder in folders:
                shutil.rmtree(f"./{folder}")

        for fg in self.feature_groupings: # Iterate through the FGs
            os.makedirs(fg.get_FG_name()) # Create a folder which has the name of the FG if it doesn't exist already
            
            os.chdir(f"./{fg.get_FG_name()}") # Enter inside of the newly created FG dir

            for AC in fg.get_rules_list(): # Iterate through the ACs in the FG & create folders with the same names
                os.makedirs(AC.get_rule_name())

                os.chdir(f"./{AC.get_rule_name()}") # Enter inside of the newly created AC dir

                for AT in AC.get_scenarios_list():
                    scen_name = AT.get_Scenario_name()
                    ac_id = AC.get_rule_ID()
                    fg_id = fg.get_FG_ID()
                    scen_id = AT.get_Scenario_ID()
                    abs_path = f"FG{fg_id}_R{ac_id}_S{scen_id}"
                    os.makedirs(scen_name)
                    os.chdir(scen_name)
                    self.stmnt_paths[abs_path] = os.getcwd() # Store the paths for the statements
                    os.chdir("..") # Go up 1 level to the AC level

                os.chdir("..") # Go up 1 level to the FG level

            os.chdir("..") # Go up 1 level to the Recordings dir level

    def begin_testing(self):
        print("Begin testing")
        self.Fill_Feature_Groupings(BTS_path = self.BTS_md_file) # Fill the feature groupings
        self.Generate_Results_Structure() # This will return the dict that has all the dict paths for the statements
        self.Execute_GWT_Scenarios() # Execute the scenarios in the feature grouping(s) & save the recordings in the statement paths
        self.Generate_Reports() # Generate the result reports

    def get_Feature_Grouping(self):
        return Feature_Grouping_Obj

    def get_AC_obj(self):
        return AC
    
    def get_AT_obj(self):
        return AT
    
    # def get_Universal_Library(self):
    #     return Universal_Library