from typing import List

from tinkoff.invest import AsyncClient, GetAccountsResponse


async def list_accounts(token) -> List:
    res = []
    async with AsyncClient(token) as client:
        r: GetAccountsResponse = await client.users.get_accounts()
        for acc in r.accounts:
            res.append({'name': acc.name, 'id': acc.id, 'type': acc.type})
            # for s in positions.securities:
            #     info: FindInstrumentResponse = await client.instruments.find_instrument(query=s.instrument_uid)
            #     market_info: GetLastPricesResponse = await client.market_data.get_last_prices(
            #         instrument_id=s.instrument_uid)
            #     res[acc.id]['positions'].append({
            #         s.instrument_uid: {
            #             'name': info.instruments[0].name,
            #             'ticker': info.instruments[0].ticker,
            #             'type': s.instrument_type,
            #             'balance': s.balance,
            #             'current_price': market_info.last_prices,
            #             'count': s.balance * market_info.last_prices,
            #         }
            #     })
    return res
