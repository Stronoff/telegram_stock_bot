from aiogram import Router


def get_handlers_router() -> Router:
    from . import export_users, info, menu, start, support, list_stocks, stock_diff_info

    router = Router()
    router.include_router(start.router)
    router.include_router(info.router)
    router.include_router(support.router)
    router.include_router(menu.router)
    router.include_router(export_users.router)
    router.include_router(list_stocks.router)
    router.include_router(stock_diff_info.router)

    return router
