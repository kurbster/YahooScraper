# YahooScraper
This program will take data from any website that you pass into the
get_data function. Currently V2.0, I am just getting data from yahoo finance.


I). Understanding the parameters of scraper.get_data:
    1). The stock name, or t, has to be passed to this funciton
    
    2). base_url and web_attrs must be passed if you are doing anything
        outside of getting the historical data.
            
    3). If you want to get data from financial pages on your url then
        set the pages kw to your dictionary.
            
    4). If you want to get the historical data you must pass in the 
        data_source=..., and start=... kw.
        
    5). If you want to get the current price then you must pass in the 
        frequency=int, and interval=int kw. Then this program will make 
        x calls to get the price every y seconds (x = interval, y = frequency)


II). Understanding the global variables in main.py:

    The web_attributes and base_url dont't change in this program
    Yahoo finance uses '?p=' in every url request 
    Therefore each page only differs in the stock name and the financial key.
    e.x
        This will get the summary for AAPL
            https://finance.yahoo.com/quote/AAPL?p=AAPL
    
        This will get the balance sheet for AAPL
            https://finance.yahoo.com/quote/AAPL/balance-sheet?p=AAPL


III). Understanding the financial_data dictionary:

    This dictionary will map a stocks name to another dictionary
    That dictionary maps the name of a dataframe then that DF
    e.x
        financial_data = {'AAPL' : {'Income'   : pd.DataFrame,
                                    'Balance'  : pd.DataFrame,
                                    'Cash'     : pd.DataFrame,
                                    'Historic' : pd.DataFrame,
                                    'Key Stats': pd.DataFrame,
                                    'Summary'  : pd.DataFrame,
                                    'Price'    : pd.DataFrame}}
                 
                                    
IV). Understanding the pages dictionary:

    pages is a dictionary that maps the user level name to the actual name of
    The page containing that data. When you pass this into get_data it will
    Iterate through each page and get the data for that based on the base_url
    And web attributes

