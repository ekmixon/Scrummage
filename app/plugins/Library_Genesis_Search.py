#!/usr/bin/env python3
import os, logging, plugins.common.General as General, plugins.common.Common as Common

class Plugin_Search:

    def __init__(self, Query_List, Task_ID, Limit=10):
        self.Plugin_Name = "Library Genesis"
        self.Concat_Plugin_Name = "libgen"
        self.Logging_Plugin_Name = General.Get_Plugin_Logging_Name(self.Plugin_Name)
        self.Task_ID = Task_ID
        self.Query_List = General.Convert_to_List(Query_List)
        self.The_File_Extension = ".html"
        self.Domain = "gen.lib.rus.ec"
        self.Result_Type = "Publication"
        self.Limit = General.Get_Limit(Limit)

    def Search(self):

        try:
            Data_to_Cache = []
            Directory = General.Make_Directory(self.Concat_Plugin_Name)
            logger = logging.getLogger()
            logger.setLevel(logging.INFO)
            handler = logging.FileHandler(os.path.join(Directory, General.Logging(Directory, self.Concat_Plugin_Name)), "w")
            handler.setLevel(logging.DEBUG)
            handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
            logger.addHandler(handler)
            Cached_Data_Object = General.Cache(Directory, self.Plugin_Name)
            Cached_Data = Cached_Data_Object.Get_Cache()

            for Query in self.Query_List:
                # Query can be Title or ISBN
                Main_URL = f"http://{self.Domain}/search.php?req={Query}&lg_topic=libgen&open=0&view=simple&res=100&phrase=1&column=def"
                Lib_Gen_Response = Common.Request_Handler(Main_URL)
                Main_File = General.Main_File_Create(Directory, self.Plugin_Name, Lib_Gen_Response, Query, self.The_File_Extension)
                if Lib_Gen_Regex := Common.Regex_Handler(
                    Lib_Gen_Response,
                    Custom_Regex=r"book\/index\.php\?md5=[A-Fa-f0-9]{32}",
                    Findall=True,
                ):
                    Current_Step = 0

                    for Regex in Lib_Gen_Regex:
                        Item_URL = f"http://{self.Domain}/{Regex}"
                        Title = General.Get_Title(Item_URL).replace("Genesis:", "Genesis |")
                        Lib_Item_Responses = Common.Request_Handler(Item_URL, Filter=True, Host=f"http://{self.Domain}")
                        Lib_Item_Response = Lib_Item_Responses["Filtered"]

                        if Item_URL not in Cached_Data and Item_URL not in Data_to_Cache and Current_Step < int(self.Limit):
                            if Output_file := General.Create_Query_Results_Output_File(
                                Directory,
                                Query,
                                self.Plugin_Name,
                                Lib_Item_Response,
                                Regex,
                                self.The_File_Extension,
                            ):
                                Output_Connections = General.Connections(Query, self.Plugin_Name, self.Domain, self.Result_Type, self.Task_ID, self.Concat_Plugin_Name)
                                Output_Connections.Output([Main_File, Output_file], Item_URL, Title, self.Concat_Plugin_Name)
                                Data_to_Cache.append(Item_URL)

                            else:
                                logging.warning(f"{Common.Date()} - {self.Logging_Plugin_Name} - Failed to create output file. File may already exist.")

                            Current_Step += 1

                else:
                    logging.warning(f"{Common.Date()} - {self.Logging_Plugin_Name} - Failed to match regular expression.")

            Cached_Data_Object.Write_Cache(Data_to_Cache)

        except Exception as e:
            logging.warning(f'{Common.Date()} - {self.Logging_Plugin_Name} - {e}')