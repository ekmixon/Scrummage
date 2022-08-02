#!/usr/bin/env python3
import plugins.common.General as General, plugins.common.Common as Common, os, logging

class Plugin_Search:

    def __init__(self, Query_List, Task_ID, Type):
        self.Plugin_Name = "AbuseIPDB"
        self.Logging_Plugin_Name = General.Get_Plugin_Logging_Name(self.Plugin_Name)
        self.Task_ID = Task_ID
        self.Query_List = General.Convert_to_List(Query_List)
        self.The_File_Extension = ".html"
        self.Domain = "abuseipdb.com"
        self.Type = Type

    def Search(self):

        try:
            Data_to_Cache = []
            Directory = General.Make_Directory(self.Plugin_Name.lower())
            logger = logging.getLogger()
            logger.setLevel(logging.INFO)
            handler = logging.FileHandler(os.path.join(Directory, General.Logging(Directory, self.Plugin_Name)), "w")
            handler.setLevel(logging.DEBUG)
            handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
            logger.addHandler(handler)
            Cached_Data_Object = General.Cache(Directory, self.Plugin_Name)
            Cached_Data = Cached_Data_Object.Get_Cache()

            for Query in self.Query_List:

                if Common.Regex_Handler(Query, Type=self.Type):
                    Search_URL = f"https://www.{self.Domain}/check-block/{Query}"
                    Responses = Common.Request_Handler(Search_URL, Filter=True, Host=f"https://www.{self.Domain}")
                    Filtered_Response = Responses["Filtered"]
                    Result_Type = self.Type

                    if self.Type == "IP":
                        Result_Type = f"{self.Type} Address"

                    Output_Connections = General.Connections(Query, self.Plugin_Name, self.Domain, f"{Result_Type} Information", self.Task_ID, self.Plugin_Name.lower())

                    if Search_URL not in Cached_Data and Search_URL not in Data_to_Cache:
                        if Output_file := General.Create_Query_Results_Output_File(
                            Directory,
                            Query,
                            self.Plugin_Name,
                            Filtered_Response,
                            Query,
                            self.The_File_Extension,
                        ):
                            Output_Connections.Output([Output_file], Search_URL, f"{self.Plugin_Name} {self.Type} | {Query}", self.Plugin_Name.lower())
                            Data_to_Cache.append(Search_URL)

                        else:
                            logging.warning(f"{Common.Date()} - {self.Logging_Plugin_Name} - Failed to create output file. File may already exist.")

                else:
                    logging.warning(f"{Common.Date()} - {self.Logging_Plugin_Name} - Failed to match regex.")

            Cached_Data_Object.Write_Cache(Data_to_Cache)

        except Exception as e:
            logging.warning(f'{Common.Date()} - {self.Logging_Plugin_Name} - {e}')