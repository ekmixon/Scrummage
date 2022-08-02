#!/usr/bin/env python3
import os, logging, plugins.common.General as General, plugins.common.Common as Common

class Plugin_Search:

    def __init__(self, Query_List, Task_ID):
        self.Plugin_Name = "Pulsedive"
        self.Logging_Plugin_Name = General.Get_Plugin_Logging_Name(self.Plugin_Name)
        self.Task_ID = Task_ID
        self.Query_List = General.Convert_to_List(Query_List)
        self.The_File_Extensions = {"Main": ".json", "Query": ".html"}
        self.Domain = "pulsedive.com"
        self.Result_Type = "Domain Information"

    def Load_Configuration(self):
        logging.info(f"{Common.Date()} - {self.Logging_Plugin_Name} - Loading configuration data.")
        if Result := Common.Configuration(Input=True).Load_Configuration(
            Object=self.Plugin_Name.lower(), Details_to_Load=["api_key"]
        ):
            return Result

        else:
            return None

    def Search(self):

        try:
            Data_to_Cache = []
            Directory = General.Make_Directory(self.Plugin_Name.lower())
            logger = logging.getLogger()
            logger.setLevel(logging.INFO)
            Log_File = General.Logging(Directory, self.Plugin_Name)
            handler = logging.FileHandler(os.path.join(Directory, Log_File), "w")
            handler.setLevel(logging.DEBUG)
            handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
            logger.addHandler(handler)
            API_Key = self.Load_Configuration()
            Cached_Data_Object = General.Cache(Directory, self.Plugin_Name)
            Cached_Data = Cached_Data_Object.Get_Cache()

            for Query in self.Query_List:

                if Common.Regex_Handler(Query, Type="Domain"):
                    API_URL = f"https://{self.Domain}/api/info.php?indicator={Query}&get=links&pretty=1&key={API_Key}"
                    Response = Common.Request_Handler(API_URL)
                    JSON_Object = Common.JSON_Handler(Response)
                    JSON_Response = JSON_Object.To_JSON_Loads()
                    JSON_Output_Response = JSON_Object.Dump_JSON()
                    Encoded_Query = General.Encoder(Query)
                    Standard_URL = f"https://{self.Domain}/indicator/?ioc={Encoded_Query}"
                    Response = Common.Request_Handler(Standard_URL)
                    Main_File = General.Main_File_Create(Directory, self.Plugin_Name, JSON_Output_Response, Query, self.The_File_Extensions["Main"])
                    Output_Connections = General.Connections(Query, self.Plugin_Name, self.Domain, self.Result_Type, self.Task_ID, self.Plugin_Name.lower())

                    if "error" in JSON_Response:
                        logging.warning(f"{Common.Date()} - {self.Logging_Plugin_Name} - Invalid response.")

                    elif API_URL not in Cached_Data and API_URL not in Data_to_Cache:
                        Title = f"{self.Plugin_Name} | {Query}"
                        if Output_file := General.Create_Query_Results_Output_File(
                            Directory,
                            Query,
                            self.Plugin_Name,
                            Response,
                            Title,
                            self.The_File_Extensions["Query"],
                        ):
                            Output_Connections.Output([Main_File, Output_file], API_URL, Title, self.Plugin_Name.lower())
                            Data_to_Cache.append(API_URL)

                        else:
                            logging.warning(f"{Common.Date()} - {self.Logging_Plugin_Name} - Failed to create output file. File may already exist.")

            Cached_Data_Object.Write_Cache(Data_to_Cache)

        except Exception as e:
            logging.warning(f"{Common.Date()} - {self.Logging_Plugin_Name} - {str(e)}")