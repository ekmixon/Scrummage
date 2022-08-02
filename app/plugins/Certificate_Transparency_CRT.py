#!/usr/bin/env python3
import os, logging, plugins.common.General as General, plugins.common.Common as Common

class Plugin_Search:

    def __init__(self, Query_List, Task_ID):
        self.Plugin_Name = "CRT"
        self.Logging_Plugin_Name = General.Get_Plugin_Logging_Name(self.Plugin_Name)
        self.Task_ID = Task_ID
        self.Query_List = General.Convert_to_List(Query_List)
        self.The_File_Extension = ".html"
        self.Domain = "crt.sh"
        self.Result_Type = "Certificate Details"

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
                if CRT_Regex := Common.Regex_Handler(Query, Type="Domain"):
                    Request = f"https://{self.Domain}/?q={Query}"
                    Responses = Common.Request_Handler(Request, Accept_XML=True, Accept_Language_EN_US=True, Filter=True, Host=f"https://{self.Domain}")
                    Response = Responses["Regular"]
                    Filtered_Response = Responses["Filtered"]

                    if "<TD class=\"outer\"><I>None found</I></TD>" in Response:
                        logging.warning(f"{Common.Date()} - {self.Logging_Plugin_Name} - Query does not exist.")

                    elif Request not in Cached_Data and Request not in Data_to_Cache:

                        try:

                            if CRT_Regex:
                                if Output_file := General.Create_Query_Results_Output_File(
                                    Directory,
                                    Query,
                                    self.Plugin_Name.lower(),
                                    Filtered_Response,
                                    CRT_Regex.group(1),
                                    self.The_File_Extension,
                                ):
                                    Output_Connections = General.Connections(Query, self.Plugin_Name, self.Domain, self.Result_Type, self.Task_ID, self.Plugin_Name.lower())
                                    Output_Connections.Output([Output_file], Request, f"Subdomain Certificate Search for {Query}", self.Plugin_Name.lower())
                                    Data_to_Cache.append(Request)

                                else:
                                    logging.warning(f"{Common.Date()} - {self.Logging_Plugin_Name} - Failed to create output file. File may already exist.")

                            else:
                                logging.warning(f"{Common.Date()} - {self.Logging_Plugin_Name} - Failed to match regular expression.")

                        except:
                            logging.warning(f"{Common.Date()} - {self.Logging_Plugin_Name} - Failed to create file.")

                else:
                    logging.warning(f"{Common.Date()} - {self.Logging_Plugin_Name} - Failed to match regular expression.")

            Cached_Data_Object.Write_Cache(Data_to_Cache)

        except Exception as e:
            logging.warning(f"{Common.Date()} - {self.Logging_Plugin_Name} - {str(e)}")