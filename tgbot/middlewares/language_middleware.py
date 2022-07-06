from typing import Tuple, Any, Optional

from aiogram.contrib.middlewares.i18n import I18nMiddleware
from aiogram.types import User

from tgbot.db import get_lang_from_db
from tgbot.config import I18N_DOMAIN, LOCALES_DIR


class ACLMiddleware(I18nMiddleware):
    async def get_user_locale(self, action: str, args: Tuple[Any]) -> Optional[str]:
        user = User.get_current()
        return await get_lang_from_db(user.id) or user.locale


i18n = ACLMiddleware(I18N_DOMAIN, LOCALES_DIR)
_ = i18n.gettext


def reg_language_middleware(dp):
    dp.setup_middleware(i18n)
