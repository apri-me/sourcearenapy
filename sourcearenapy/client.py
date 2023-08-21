import asyncio
#
import aiohttp
#
from sourcearenapy import exceptions


class AsyncClient:
    BASE_URL = "https://sourcearena.ir/api/"
    session: aiohttp.ClientSession
    token: str
    loop: asyncio.BaseEventLoop
    def __init__(self, token: str) -> None:
        self.token = token
        self.loop = self._get_loop()
        self.session = self._init_session()

    def _init_session(self) -> aiohttp.ClientSession:
        session = aiohttp.ClientSession(
            loop=self.loop,
        )
        return session

    async def _get(self, **kwargs) -> dict|list:
        kwargs["token"] = self.token
        async with self.session.get(self.BASE_URL, params=kwargs) as response:
            return await self._handle_response(response)

    async def get_candle(self, symbol: str, period: str) -> list|dict:
        """قیمت های مورد نیاز نمودار شمعی شامل اولین قیمت، آخرین قیمت، پایینترین قیمت و بالاترین قیمت از تاریخ فروردین ۱۳۹۸ به بعد 
        
        symbol: نام نماد (مثال : شپنا) 
        
        period: دوره (مثال : 1394/04)
        """
        res = await self._get(history=symbol, period=period)
        return res

    async def get_price_history(self, symbol: str, n: int) -> list|dict:
        """تاریخچه قیمت نماد n روز اخیر
        
        مناسب برای محاسبه میانگین هقتگی و ماهانه احراز هویت
        
        symbol: نام نماد (مثال : شپنا) 

        n: تعداد روز
        """
        res = await self._get(name=symbol, days=n)
        return res

    async def get_all_symbols_information(self, _type:int=2, date_str:str=None) -> list:
        """اطلاعات همه نماد های بورسی و فرابورسی، صندوق، حق تقدم، معاملات بلوکی و اختیارمعامله که در آخرین روز معاملاتی بازار، معامله شدند.

        date_str: yyyy/mm/dd

        _type:
    
            همه‌ی نماد‌ها: 2

            بورس و فرابورس: 0
"""
        if date_str is not None:
            res = await self._get(type=_type, time=date_str, all="-")
        else:
            res = await self._get(type=_type, all="-")
        if type(res) == type(dict()) and "Error" in res.keys():
            raise exceptions.OffDayException(f"The day {date_str} is off")
        return res

    async def get_single_symbol_information(self, symbol: str, date_str:str=None):
        """اطلاعات تکی نماد
        
        اطلاعات همه نماد های بورسی و فرابورسی به صورت لحظه ای یا به تاریخ مشخص(از تاریخ خرداد ماه سال 1399) احراز هویت
        
        symbol: نام نماد (مثال : شپنا) 

        date_str: yyyy/mm/dd

        """
        if date_str is not None:
            res = await self._get(name=symbol, time=date_str)
        else:
            res = await self._get(name=symbol)
        if type(res) == type(dict()) and "Error" in res.keys():
            raise exceptions.OffDayException(f"The day {date_str} is off")
        return res
    
    async def get_adjusted_daily_candles(self, symbol: str, from_date: str, to_date: str, adjust_type:int=1) -> list|dict:
        """اطلاعات قیمتی تعدیل شده (کندل روزانه)
        
        قیمت های مورد نیاز نمودار شمعی شامل اولین قیمت، آخرین قیمت، پایینترین قیمت و بالاترین قیمت،حجم معامله و ارزش معامله
        
        این اندپوینت به صورت مجزا ارائه می شود. برای فعال سازی آن به پشتیبانی مراجعه کنید

        symbol: نام نماد (مثال : شپنا) 
        
        from, to: yyyymmdd
        
        adjust_type: 
        
         	1= افزایش سرمایه و تقسیم سود
             
            2= افزایش سرمایه
            
            3= تقسیم سود"""
        kwargs = {
            "name": symbol,
            "from": from_date,
            "to": to_date,
            "type": adjust_type,
            "adjusted": "-"
        }
        res = await self._get(**kwargs)
        return res

    @staticmethod
    async def _handle_response(response: aiohttp.ClientResponse):
        if not str(response.status).startswith('2'):
            raise exceptions.SourceArenaApiException(response, response.status, await response.text())
        try:
            return await response.json(content_type=None)
        except ValueError:
            txt = await response.text()
            raise exceptions.SourceArenaRequestException(f'Invalid Response: {txt} \nURL : {response.url}')

    @staticmethod
    def _get_loop():
        """check if there is an event loop in the current thread, if not create one
        inspired by https://stackoverflow.com/questions/46727787/runtimeerror-there-is-no-current-event-loop-in-thread-in-async-apscheduler
        """
        try:
            loop = asyncio.get_event_loop()
            return loop
        except RuntimeError as e:
            if str(e).startswith("There is no current event loop in thread"):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                return loop
            else:
                raise
